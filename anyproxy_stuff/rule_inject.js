'use strict';
var fs = require('fs');
var url = require('url');
var sd = require('silly-datetime')
// TODO: 可以使用一个同步post代替
var request = require('sync-request');  // 同步get
var request_json = require('request-json');   // 异步post
var localPng = fs.readFileSync('/log/1.png');   // 所在盘绝对路径


module.exports = {

  summary: 'Rule Inject...',

  /**
   *
   *
   * @param {object} requestDetail
   * @param {string} requestDetail.protocol
   * @param {object} requestDetail.requestOptions
   * @param {object} requestDetail.requestData
   * @param {object} requestDetail.response
   * @param {number} requestDetail.response.statusCode
   * @param {object} requestDetail.response.header
   * @param {buffer} requestDetail.response.body
   * @returns
   */
  *beforeSendRequest(requestDetail) {
    const localResponse = {
      statusCode: 200,
      header: {'Content-Type': 'image/jpeg'},
      body: localPng
    };
    // capsane 2018.04.09 return local picture: 图片和评论区用户头像
    if(/mmbiz\.qpic\.cn/i.test(requestDetail.url) || /wx\.qlogo\.cn/i.test(requestDetail.url) ) {
      return {
        response: localResponse
      };
    }

    // 笨死了，在这里延迟发送post(num)的请求, TODO: 感觉不需要
    // else if(/\/mp\/getappmsgext\?f=json/i.test(requestDetail.url)) {
    //   console.log("`````````````````````````````delay the post(num) request for 0.2s ''''''''''''''''''''''''''''''.............................")
    //   return new Promise((resolve, reject) => {
    //     setTimeout(() => {
    //       resolve(requestDetail);
    //     }, 300);
    //   });
    // }

    // 历史请求也需要delay，不然在最后一篇文章get之后，会请求

    else {
      return null;
    }
  },


  /**
   *
   *
   * @param {object} requestDetail
   * @param {object} responseDetail
   */
  *beforeSendResponse(requestDetail, responseDetail) {
    var pathname = url.parse(requestDetail.url).pathname;
    // 只对hostname为mp.weixin.qq.com/的response进行处理
    if (/mp\.weixin\.qq\.com\//i.test(requestDetail.url)) {

      try {
        var header = responseDetail.response.header;
        const resbody = responseDetail.response.body.toString();


        // 历史文章列表
        if (/mp\/profile_ext\?action=home/i.test(requestDetail.url)) {
          console.log(sd.format(new Date(), '--------------[YYYY-MM-DD HH:mm:ss]') + " 处理历史文章列表响应.......................................................");
          // 修改响应头
          responseDetail.response.header['content-type'] = 'text/html; charset=UTF-8';
          delete responseDetail.response.header['content-security-policy'];
          delete responseDetail.response.header['content-security-policy=report-only'];

          // FIXME: 事实证明，B -> A
          // FIXME: 必须要保证A -> B ?

          // A. http, POST数据, 非同步, server读取文章url, 入队列
          var client = request_json.createClient('http://localhost:6210/');
          var data = {htmlbody: resbody, requrl: requestDetail.url};
          client.post('recent', data, function(err, res, body) {
            console.log("post history list: " + res.statusCode, body);
          })


          // B. sync-request, GET返回的JS，同步

          var res = request('GET', 'http://localhost:6210/history_next');  // 阻塞
          var finalJS = res.getBody();
          console.log(sd.format(new Date(), '--------------[YYYY-MM-DD HH:mm:ss]') + " finalJS: " + finalJS);

          /*
          // capsane 2018.04.10
          // C. sync-request, POST, 同步
          // FIXME: ENAMETOOLONG, 应该是resbody太长了
          console.log("&&&&&&&&&&&&&&&&&&&&&&&&&同步POST&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
          var res = request('POST', 'http://localhost:6210/test', {
            json: {htmlbody: resbody, requrl: requestDetail.url}
            // json: {requrl: requestDetail.url}
          });
          var finalJS = res.getBody('utf8');
          console.log("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT: test finalJS: " + finalJS);
          */

          // 注入finalJS
          var content = resbody.replace("<!--headTrap<body></body><head></head><html></html>-->","").replace("<!--tailTrap<body></body><head></head><html></html>-->","");
          content = content.replace("</body>",finalJS + "\n</body>");			
          
          var buffer = new Buffer(content);
          responseDetail.response.body = buffer;
          return responseDetail;
        }


        // 文章内容 
        else if (/\/s\?__biz=/i.test(requestDetail.url)) {
          console.log(sd.format(new Date(), '--------------[YYYY-MM-DD HH:mm:ss]') + " 处理文章内容响应:.............................................................");
          console.log("requestDetail.url: " + requestDetail.url);
          // console.log("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< May Be Error : change header <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<");

          // A. sync-request, GET返回的JS，同步。Server会从文章队列中弹出当前url对应的文章
          // console.log("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< May Be Error : sync-request <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<");
          // TODO: 传递requestDetail.url参数
          var res = request('GET', 'http://localhost:6210/article_next');
          var finalJS = res.getBody();

          // FIXME: 如何确保顺序：get(js)->post(content)
          // B. http, POST数据, 非同步。Server会修改的Article的content信息
          var client = request_json.newClient('http://localhost:6210/');
          var data = {htmlbody: resbody, requrl: requestDetail.url};
          client.post('detail', data, function(err, res, body) {
            console.log(sd.format(new Date(), '--------------[YYYY-MM-DD HH:mm:ss]') + " post article detail html content: " + res.statusCode, body);
          })

          // 注入finalJS
          var content = resbody.replace("<!--headTrap<body></body><head></head><html></html>-->","").replace("<!--tailTrap<body></body><head></head><html></html>-->","");
          content = content.replace("</body>",finalJS + "\n</body>");   

          // TODO: 尽量保证requst(js)和post(content)在下面的post(num)之前执行
          // 修改响应头
          responseDetail.response.header['content-type'] = 'text/html; charset=UTF-8';
          delete responseDetail.response.header['content-security-policy'];
          delete responseDetail.response.header['content-security-policy=report-only'];

          var buffer = new Buffer(content);
          responseDetail.response.body = buffer;
          // TODO: 或许需要在这里延迟返回
          return responseDetail;
        }

        // read, like num
        // FIXME: url的匹配
        else if (/\/mp\/getappmsgext\?/i.test(requestDetail.url)) {
          // TODO: 不如多打印几行，尽量保证上面的get(js)和post(content)在Server执行完，至少请求先到达Server
          console.log(sd.format(new Date(), '--------------[YYYY-MM-DD HH:mm:ss]') + " 处理阅读数据的响应********************************************************************");
          // C. http, POST数据, 非同步
          // 耗时操作，例如一段为真的正则表达式或者除法
          var client = request_json.newClient('http://localhost:6210/');
          var data = {statistic: resbody, requrl: requestDetail.url};
          client.post('num', data, function(err, res, body) {
            console.log(sd.format(new Date(), '--------------[YYYY-MM-DD HH:mm:ss]') + " post read like num: " + res.statusCode, body);
          })
        }

        // 其他请求不做修改
        else {
          return null;
        }
      } catch(e) {
        console.error(e);
        return null;	// 不做任何处理
      } finally {
        return responseDetail;
      }
    }
    else {
      return null;
    }
  },


  /**
   * default to return null
   * the user MUST return a boolean when they do implement the interface in rule
   *
   * @param {any} requestDetail
   * @returns
   */
  *beforeDealHttpsRequest(requestDetail) {
    return true;
  },

  /**
   *
   *
   * @param {any} requestDetail
   * @param {any} error
   * @returns
   */
  *onError(requestDetail, error) {
    return null;
  },


  /**
   *
   *
   * @param {any} requestDetail
   * @param {any} error
   * @returns
   */
  *onConnectError(requestDetail, error) {
    return null;
  },


  /*
  // POST发送数据
  httpPost: function(reqUrl, body, path) {
    body  ="农夫山泉下有知";
    var http = require('http');
    var data = {
      "data": body,
      "requrl": "this is a reqUrl"
    };
    // data字典
    // var content = require('querystring').stringify(data);
    var content =JSON.stringify(data);
    // var content = body;
    // capsane
    // var content = "农夫山泉下有知"
    var options = {
      method: 'POST',
      host:   'localhost',
      port:   6210,
      path:   path,
      headers: {
        'Content-Type': 'application/json; charset=UTF-8',
        // 'Content-Type': 'text/html; charset=UTF-8',
        'Content-Length': content.length
      }
    };
    var response = "";

    var req = http.request(options, function(res) {
      res.setEncoding('utf8');
      res.on('data', function(chunk) {
        response += chunk;
      });
      res.on('end', function() {
        console.log("POST done.")
        console.log(response);
      })
    });

    req.on('error', function(e) {
      console.log(e.message);
      console.log("Problem with POST: " + e.request);
    })
    console.log(content);
    req.write(content);
    console.log(content);
    req.end();
  },
  */
  

  /*
  // 对自己服务器的POST：向服务器传递html，请求返回需要注入的JS
  // TODO: 直接传递Buffer还是html
  // 需要注意线程同步问题，请求自己的服务器毕竟还是耗时的，NodeJs的回调函数
  httpPost: function(reqUrl, data, path, callback) {
    var http = require('http');
    var data = {
      data: data,
      req_url: reqUrl
    };
    // data字典
    var content = require('querystring').stringify(data);
    var options = {
      method: 'POST',
      host:   'localhost',
      port:   6210,
      path:   path,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Content-Length': content.length
      }
    };
    var response = "";
    // 
    const req = http.request(options, function(res) {
      res.setEncoding('utf8');
      res.on('data', function(chunk) {
        // TODO: 自己的服务器可以选择返回一个JS字符串
        response += chunk;
      });
      // 获得全部response之后，才会触发下面的回调函数。但是我怎么确定何时传输完成了呢
      res.on('end', function() {
        // 这里httpPost已经执行完了,通过回调将response传递出去！！！
        if (callback) {
          callback(response);
        }
        return response;
      })
    });

    req.on('error', function(e) {
      console.log(e.message);
      console.log("Problem with request: " + e.request);
    })

    req.write(content);
    req.end();
    // 直接执行了我也是。。。。
    console.log("222222222222222222222222222222222222222222222222222222222222222222httpPost()返回的js为：" + response+ "222222222222222222222222222222222222222222222222222222222222222222");
    // return response;
  },
*/

};


