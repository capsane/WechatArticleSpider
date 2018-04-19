# 业务逻辑

> 输入：公众号列表(name, id)

- 公众号历史文章:

```text
本次发布的共同信息：
nickname, biz, can_message_continue, is_subscribed
datetime, type(49), fakeid

每篇文章的信息：
author, content_url, copyright_stat, cover, del_flag, digest, fileid, source_url, title

无法获得的信息：
content
read_num, like_num

```

- 文章内容requrl：biz+mid+idx唯一确定

能够从响应中提取的信息：

```text
content
appuin(biz), nickname, appmsg_type(9), publish_time(day), msg_title, msg_desc, msg_link, appmsgid(mid), msg_daily_idx, 
source_encode_biz(原创biz), source_mid, source_idx, source_biz = "2390849143"
copyright_stat = "2" * 1, appmsg_token， 
```

- 阅读数据requrl：由微信客户端在接收到文章内容的响应之后自动发送，可以通过文章内容中的appmsg_token+else确定。

```text
read_num, like_num
```


## 1.公众号biz批量获取 

> 使用清博：查询microhugo或者hugo

http://www.gsdata.cn/query/wx?q=hugo

查看返回的HTML：

清博的排序：广告、影响因子排序。所以需要同时记录收集到的biz和nickname，确定是否准确。一般取第一条就可以了。

```html
<input type="hidden" class="biz" value="MjM5MzI5NzQ1MA==">
<a target="_blank" id="nickname" href="/rank/wxdetail?wxname=bQWBlDjScJmq9iondgW5d2v1">HUGO</a>
```

> 登录清博，在请求中添加cookie。

```python
def get_biz_with_cookie(name):
    url = "http://www.gsdata.cn/query/wx?q="+name
    cookie = "bdshare_firstime=1522394312301; acw_tc=AQAAAGNfbmmHGg0Aw9vMb037nC036xBZ; _csrf-frontend=1dcbc8b29bd8141757ca062ff538f394f91a604c968a2e0356e8607b8d88f605a%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22_csrf-frontend%22%3Bi%3A1%3Bs%3A32%3A%225jLN4NmHiyYU0mmNMmpSl82DLSa6eyGh%22%3B%7D; Hm_lvt_293b2731d4897253b117bb45d9bb7023=1522064255,1522394309,1522403335,1522506280; _gsdataCL=WyIxMjEwMDIiLCIxNTYxMTUzMzc3NiIsIjIwMTgwMzMxMjIyNDUyIiwiMWZkNzE3ZTJjYjEyZTk2MGVjYThmY2NmNGVjNjNiOGIiLDk3NDI4XQ%3D%3D; PHPSESSID=qhq4qqce7non5f0045dcbtjgm7; _identity-frontend=3c96cbe59e07d6bfac88b77c83fe9af11afd2242dc10460faa77882df8b0561da%3A2%3A%7Bi%3A0%3Bs%3A18%3A%22_identity-frontend%22%3Bi%3A1%3Bs%3A26%3A%22%5B%22121002%22%2C%22test+key%22%2C3600%5D%22%3B%7D; Hm_lpvt_293b2731d4897253b117bb45d9bb7023=1522506307"
    headers = {
        "Host": "www.gsdata.cn",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Referer": "http://www.gsdata.cn/query/wx?q=hugo",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cookie": cookie
    }
    r = requests.get(url, headers=headers)
    print(r.text)
    bsObj = BeautifulSoup(r.text, "html.parser")
    # 解析biz：<input type="hidden" class="biz" value="MjM5MzI5NzQ1MA==">
    tagBiz = bsObj.find(name='input', attrs={"class": "biz"})
    if not tagBiz:
        print("找不到biz标签, 请尝试更新cookie!!")
    else:
        biz = tagBiz['value']
    # 解析nickname: <a target="_blank" id="nickname" href="/rank/wxdetail?wxname=bQWBlDjScJmq9iondgW5d2v1">HUGO</a>
    tagName = bsObj.find(name='a', attrs={"target": "_blank", "id": "nickname"})
    nickname = tagName.text
    return biz, nickname
```

## 2.AnyProxy

### 2.1 AnyProxy介绍

### 2.2 rule_inject.js

#### 2.2.1 beforeSendRequest(requestDetail)

> 修改微信客户端发送的请求 

```js
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
    // 其他请求不做修改
    else {
      return null;
    }
  },
```

#### 2.2.2 beforeSendReposne(requestDetail, responseDetail)

> 修改微信服务器返回的内容

```js

  *beforeSendResponse(requestDetail, responseDetail) {
    var pathname = url.parse(requestDetail.url).pathname;
    // 只对hostname为mp.weixin.qq.com/的response进行处理
    if (/mp\.weixin\.qq\.com\//i.test(requestDetail.url)) {
      try {
        var header = responseDetail.response.header;
        const resbody = responseDetail.response.body.toString();

        // 历史文章列表
        if (/mp\/profile_ext\?action=home/i.test(requestDetail.url)) {
          console.log("处理历史文章列表.......................................................");
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
          console.error("finalJS: " + finalJS);


          // 注入finalJS
          var content = resbody.replace("<!--headTrap<body></body><head></head><html></html>-->","").replace("<!--tailTrap<body></body><head></head><html></html>-->","");
          content = content.replace("</body>",finalJS + "\n</body>");			
          
          var buffer = new Buffer(content);
          responseDetail.response.body = buffer;
          return responseDetail;
        }

        // 文章内容 
        else if (/\/s\?__biz=/i.test(requestDetail.url)) {
          console.log("处理文章内容url:.............................................................");
          console.log(requestDetail.url);
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
            console.error("post article detail html content: " + res.statusCode, body);
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
          console.log("url请求的是  like num********************************************************************");
          // C. http, POST数据, 非同步
          // 耗时操作，例如一段为真的正则表达式或者除法
          var client = request_json.newClient('http://localhost:6210/');
          var data = {statistic: resbody, requrl: requestDetail.url};
          client.post('num', data, function(err, res, body) {
            console.error("post read like num: " + res.statusCode, body);
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

```

> 根据微信客户端发送的请求分别进行处理：

**1历史文章**

- get(js)：GET请求Server的history_next页面

使用sync-request，同步请求，因为需要根据Server返回的js才能给微信客户端返回响应

- post(history_html)：POST请求Server的recent页面，服务器处理history_html


**2文章内容**

- get(js)：同样使用sync-request请求Server返回需要注入的js，即该文章内容出来完之后需要跳转的页面
- post(content_html)：设计上这一步需要在get(js)之后，理论上sync-request会保证Server处理完并返回注入js的响应之后才会继续执行

**3阅读数据**

- post(num)在2文章内容的响应返回之后，微信客户端才会自动发送阅读数据的请求。拦截其响应并post给Server处理

**4执行顺序**

- **历史文章**，设计上最好能够保证post(history_html) -> get(js)，因为我们需要将文章列表入队列，然后再取出一篇用其content_url作为需要返回的js。但是这个不重要， 每次处理多个公众号然后再访问文章就好。
- **文章内容**，需要严格保证**get(js)** -> **post(content_html)** -> **post(num)**的执行顺序，以及在Server的处理顺序。

> get(js) -> post(content_html)可以由sync-reques保证；post(content_html)也是默认保证的，因为只有在2文章内容响应返回后微信客户端才会发送3阅读内容请求。

> **问题**<br>
1.如果可以使用同步post，那么get(js)和post(html)就可以简化为一次网络请求了。但是nodejs的同步操作真的是头大，望高手指点<br> 2.有时候对于同一篇文章，微信客户端会发送两次request，这在我自己的Server端就爆炸了：默认请求一个文章内容就会弹出一个对应的Article的啊。感觉可以优化。**如果不使用Queue，使用Dictory呢?无序啊，。但是不知道如果两次都响应，会不会两个都跳转，应该不会，后一个应该会覆盖掉前一个响应**<br> 3.最蛋疼的问题，昨天碰到有个bug，Anyproxy中明明只收到了一个文章内容请求，但却做了两次处理。相当于对于同一个url执行了两次beforeSendReposne()。因为**微信服务器确实返回了两次响应**？？？疯了吧

```
[AnyProxy Log][2018-04-13 20:40:28]: received request to: GET mp.weixin.qq.com/s?__biz=MjM5NjMxMDYwMQ==&mid=2651947745&idx=2&sn=035303ccc78406caa5e8a75019289366&chksm=bd0e19c78a7990d18d9ebd92fa2f149760b6d2de8039f4cea0e3e60b498231cbb9c33ba465dc&scene=27&ascene=3&devicetype=android-17&version=26060536&nettype=WIFI&abtest_cookie=AwABAAoACwAMAAkAl4oeAKaKHgA%2Bix4ASIseAHeLHgCpjB4A4IweAAONHgAFjR4AAAA%3D&lang=zh_CN&pass_ticket=7jhHpB0TwqEBLwHTUWR3lUtcK4GllRxeEtd5gyaDu7jTujAfb%2B6Pf6Pu5IWqeh40&wx_header=1
处理文章内容url:.............................................................
https://mp.weixin.qq.com/s?__biz=MjM5NjMxMDYwMQ==&mid=2651947745&idx=1&sn=2f5c9a82a393adce271b9b1003f68dd6&chksm=bd0e19c78a7990d1b6f7ea5758adb4b0f52841065a9fa892dbe296ff0493bf49798c5686fe92&scene=27&ascene=3&devicetype=android-17&version=26060536&nettype=WIFI&abtest_cookie=AwABAAoACwAMAAkAl4oeAKaKHgA%2Bix4ASIseAHeLHgCpjB4A4IweAAONHgAFjR4AAAA%3D&lang=zh_CN&pass_ticket=7jhHpB0TwqEBLwHTUWR3lUtcK4GllRxeEtd5gyaDu7jTujAfb%2B6Pf6Pu5IWqeh40&wx_header=1
post article detail html content: 200 None
处理文章内容url:.............................................................
https://mp.weixin.qq.com/s?__biz=MjM5NjMxMDYwMQ==&mid=2651947745&idx=2&sn=035303ccc78406caa5e8a75019289366&chksm=bd0e19c78a7990d18d9ebd92fa2f149760b6d2de8039f4cea0e3e60b498231cbb9c33ba465dc&scene=27&ascene=3&devicetype=android-17&version=26060536&nettype=WIFI&abtest_cookie=AwABAAoACwAMAAkAl4oeAKaKHgA%2Bix4ASIseAHeLHgCpjB4A4IweAAONHgAFjR4AAAA%3D&lang=zh_CN&pass_ticket=7jhHpB0TwqEBLwHTUWR3lUtcK4GllRxeEtd5gyaDu7jTujAfb%2B6Pf6Pu5IWqeh40&wx_header=1
post article detail html content: 200 None
```


---

## 3.Web.py

### 3.1 Server功能

响应Anyproxy的get(js)

处理Anyproxy的post(history_html), post(content_html), post(num)发送的数据，分别提取历史文章list，解析文章内容，解析阅读数据，最后将文章信息入库

### 3.2 

## 4.数据包分析

### 4.1公众号数据请求解析

#### 4.1.1 点击公众号历史文章:

原始url：

https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5MzI5NzQ1MA==&scene=124&devicetype=android-17&version=26060533&lang=zh_CN&nettype=WIFI&a8scene=3&pass_ticket=aC9CtwpwGejdIKyLt67rMuXJw6m3zOZUmJeOX3f8DXRKQyhtU6sAK5kBIDNs9oL5&wx_header=1

简化为:

https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5MzI5NzQ1MA==&scene=124#wechat_redirect

简化的原因：本方案通过在微信服务器返回的html中添加JS脚本，实现后续的自动化数据爬

```js
// 修改微信服务器返回的数据
    /**测试body的存储类型为：Buffer */
    // var url = requestDetail.url
    // if  (/mp\/profile_ext\?action=home/i.test(requestDetail.url)) {
    //   var newRequest = requestDetail.requestData;
    //   var newResponse = responseDetail.response.body;
    //   console.log(newResponse);
    //   console.log("***********************************----------------------------------------------------+++++++++++++++++++++++++++++++++++++++***************************************");
    //   // 存储为Buffer，转换为String
    //   console.log(newResponse.toString());
    //   // 保存到文件的时候自动存储为String
    //   fs.appendFileSync(log, "response:-------------------------------------------------------------------------\n " + newResponse + "\n", 'utf-8', function(err) {
    //     if(err) throw err;
    //     console.log("responseData is saved!");
    //   });
    // }

  *beforeSendResponse(requestDetail, responseDetail) {
    // 服务端返回的JS
    function callback (responseFromMyServer) {
      return responseFromMyServer;
    }

		try {
      var header = responseDetail.response.header;
      const body = responseDetail.response.body.toString();

			// 历史文章列表
			if (/mp\/profile_ext\?action=home/i.test(requestDetail.url)) {
        // 修改响应头
        responseDetail.response.header['content-type'] = 'text/html; charset=UTF-8';
        delete responseDetail.response.header['content-security-policy'];
        delete responseDetail.response.header['content-security-policy=report-only'];

        // A. http, POST数据, 非同步
        this.httpPost(requestDetail.url, body, "/post.html");

        // B. sync-request, GET返回的JS，同步
        var res = request('GET', 'http://localhost:6210/get.html');
        var finalJS = res.getBody();

        // 注入finalJS
        var content = body.replace("<!--headTrap<body></body><head></head><html></html>-->","").replace("<!--tailTrap<body></body><head></head><html></html>-->","");
        content = content.replace("</body>",finalJS + "\n</body>");			
        
        var buffer = new Buffer(content);
				responseDetail.response.body = buffer;
				return responseDetail;
			}
			else {
				return null;
			}
		} catch(e) {
			console.log(e);
			return null;	// 不做任何处理
    } finally {
      return responseDetail;
    }
  },

```

**需要注意的问题**

- responseDetail.reponse.body的存储类型为**Buffer**
- 尝试搭建一个webpy服务器，刚好解析的函数已经写好了



**公众号信息**

可由上面链接返回的HTML中提取：**名称**, **头像地址**

```js
    var can_msg_continue = '1' * 1;
    var headimg = "http://wx.qlogo.cn/mmhead/Q3auHgzwzM58Frfaic1TBsibCNBiapHWzzodTm9vSqVL2nZ973e0hqYqw/0" || "";
    var nickname = "HUGO" || "";
    var is_banned = "0" * 1;
    var __biz = "MjM5MzI5NzQ1MA==";
    var next_offset = "10" * 1;
```

- 认证信息：已关注的公众号不会返回认证信息

### 4.2 数据解析

#### 4.2.1 html格式的文章列表

```
var msgList = 
<!-- 近十天文章列表 -->
list: [
		{comm_msg_info：{}, app_msg_ext_info：{头条文章, multi_app_msg_item_list：[{分栏文章1}, {分栏文章2}], }}, 
		{comm_msg_info: }} 
	  ]
```

正则提取var msgList = 参数后的信息; 

> get_recent_article_url.py

```python
# 返回list，长度应该为10，lsist[0]为最近一天的全部图文
def get_history_list(html):
    msg_dict = None
    # 从文件读取HTML
    # bs = BeautifulSoup(open(filename, encoding="utf-8"), "html.parser")
    bs = BeautifulSoup(html, "html.parser")
    # 查找 type属性为text/javascript && tag名称为script && 字符串内容中包含"var msgList"的<script>Tag
    script = bs.find(name="script", attrs={"type": "text/javascript"}, text=re.compile("var msgList"))
    content = script.text
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if re.match("var msgList", line):
            msg_list = re.search("{.*}", line).group()
            msg_list = msg_list.replace("&quot;", "\"").replace("&amp;", "&").replace("&amp;", "&")
            # 公众号历史文章信息字典
            msg_dict = json.loads(msg_list)
            break
    # 返回近十天的历史文章列表
    return msg_dict['list']
```

#### 4.2.2 json格式的文章列表

有无更多文章可由var can_msg_continue = '1' * 1;提取。

若有更多文章，下拉列表(下滑)，微信服务器会返回json。

目前并未实现

#### 4.2.3 历史文章解析

**由历史文章列表中可提取出各个文章的URL**

取出的url：

```
http:\\/\\/mp.weixin.qq.com\\/s?__biz=MjM5MzI5NzQ1MA==&amp;amp;mid=2654644732&amp;amp;idx=1&amp;amp;sn=a84971cc61c2c4c745bf57fe75dbe72f&amp;amp;chksm=bd572cb98a20a5af22081cba0afe7a76e2c25c87faa4cccf462f6a949f63e7a60de89cc54598&amp;amp;scene=27#wechat_redirect
```

> \\为反义字符; 
> &amp;		就是	&
> &quote;   就是  	"

两次url解码：

```
http://mp.weixin.qq.com/s?__biz=MjM5MzI5NzQ1MA==&mid=2654644732&idx=1&sn=a84971cc61c2c4c745bf57fe75dbe72f&chksm=bd572cb98a20a5af22081cba0afe7a76e2c25c87faa4cccf462f6a949f63e7a60de89cc54598&scene=27#wechat_redirect
```


- _biz: 公众号id
- mid: 图文消息id，同一天的id一样！！！
- idx: 发布的第几栏文章
- mid与idx拼接确定唯一一篇文章，所以同一篇文章，今天和明天的mid是不同的吗？

#### 4.2.A NodeJs服务器

```js
var http = require('http')
var url = require('url')
var fs = require('fs')

http.createServer(function(req, res) {
    var pathname = url.parse(req.url).pathname;
    var post = "";

    console.log("Request for " + pathname + " received.");

    // GET
    if (pathname == "/get.html") {
        console.log("Case: get");
        var js = '<script type="text/javascript">var url = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5OTIwODMzMQ==&scene=124#wechat_redirect";\
            setTimeout(function() {window.location.href=url;}, 10000);</script>';          
        res.write(js);
        res.end();
    }

    // post, 读取data
    else if (pathname == "/post.html") {
        console.log("Case: post");
        // 读取POST数据
        req.on('data', function(chunk) {
            post += chunk;
        });
    
        req.on('end', function() {
            console.log("POST 接收完毕: ");
            post = require('querystring').parse(post);
            // console.log(post['data']);
            console.log(post['requrl']);
            
            // 一定要写在这里，不然无法获得全部的post数据!!!!!!
            res.writeHead(200, {'Content-Type': 'text/html; charset=utf8'});
            res.write("Hello Anyproxy.");
            res.end();

        });


        // 返回JS
        // var responseJson = {
        //     "js": "\'<script type=\"text/javascript\">var url = \"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5OTIwODMzMQ==&scene=124#wechat_redirect\"; setTimeout(function() {window.location.href=url;}, 10000);</script>\'", 
        //     };
        // var json = JSON.stringify(responseJson);

    
    }

}).listen(6210);

console.log("Server running at http://localhos:6210");

```

#### 4.5.B Web.py服务器






#### 4.2.4 点赞量、阅读量

当访问文章详情时，即请求上面的url后，微信客户端会**主动**发起阅读量和点赞量的请求，请求地址如下(不用关心)，需要截取返回的json

```
https://mp.weixin.qq.com/mp/getappmsgext?__biz=MjM5MzI5NzQ1MA==&appmsg_type=9&mid=2654644789&sn=9c693340da18ca1a92c0c3846b0c2a2a&idx=1&scene=38&title=26%E5%B2%81%E5%A5%B3%E5%AD%A9%E6%80%80%E5%AD%955%E6%9C%88%E6%9F%A5%E5%87%BA%E7%99%8C%E7%97%87%EF%BC%8C%E5%A5%B9%E7%9A%84%E9%80%89%E6%8B%A9%E8%AE%A9%E6%97%A0%E6%95%B0%E4%BA%BA%E6%B3%AA%E5%A5%94%EF%BC%9A%E6%AF%8F%E4%B8%80%E4%B8%AA%E6%AF%8D%E4%BA%B2%E5%92%8C%E5%AD%A9%E5%AD%90%E4%B9%8B%E9%97%B4%EF%BC%8C%E9%83%BD%E6%98%AF%E7%94%9F%E6%AD%BB%E4%B9%8B%E4%BA%A4%EF%BC%81&ct=1522413397&abtest_cookie=AwABAAoACwAMAAkAl4oeAKaKHgA+ix4ASIseAHeLHgBvjB4AkIweAKmMHgCujB4AAAA=&devicetype=android-17&version=/mmbizwap/zh_CN/htmledition/js/appmsg/index3ca156.js&f=json&r=0.48851961619220674&is_need_ad=1&comment_id=215102812210692096&is_need_reward=0&both_ad=0&reward_uin_count=0&msg_daily_idx=1&is_original=0&uin=777&key=777&pass_ticket=aC9CtwpwGejdIKyLt67rMuXJw6m3zOZUmJeOX3f8DXRKQyhtU6sAK5kBIDNs9oL5&wxtoken=777&devicetype=android-17&clientversion=26060533&appmsg_token=950_1%252BGTdRglX%252BHjq0N5Ire-NgnFCX8_xhLmeYU6d50EfVKqI0pgPVzDuTMrGDmL3bJwbe52yoWCM3QX9T8h&x5=0&f=json
```

**如何截获返回的json?**

#### 4.2.5 评论信息

暂不考虑

4.2.4的主动请求的返回数据包中有"comment_enabled":1参数，微信客户端就会**主动**发起评论的请求，返回json


### 5 技术思路

> 使用中间人的方式，截获微信服务端到客户端的数据，处理入库。然后修改返回的数据，注入js？，传递给客户端，实现自动翻页？，爬取更多

#### 5.1 anyproxy代码思路

修改rule_default.js


#### 5.2 server代码思路

> 通过anyproxy截获数据到服务端，进行数据处理，入库

1. webpy框架
2. 正则处理公众号信息
3. 处理文章列表
	1. 解析文章列表
	2. 文章信息存入缓存
	3. 将文章url添加到待抓取的url地址池队列
	4. 判断是否可以下拉显示更多，继续添加url
	5. 判断url地址池是否为空，非空则pop，嵌入js，返回到anyproxy，anyproxy会继续将带有js的数据返回给微信客户端，实现了自动跳转
	<script>setTimeout(function(){window.location.href="跳转地址";}, 10000;)</script>>
	6. 若队列为空，则去库中取下一个待爬取公众号历史链接(biz参数)。
	https://mp.weixin.qq.com/profile_ext?action=home&_biz=ASDwerASDSF==&scene=124#wechat_redirect

4. 文章内容获取

步骤3已经向微信客户端注入了自动跳转文章详情的url的js，到设定时延后，会接收到文章详情的数据，正则提取正文信息，若正文存在，则添加到文章信息缓存。否则可能为被验证为不实的文章，此时客户端不会发起阅读量请求，直接将该文章信息整体入库，从缓冲区中删除。？？？？


---

### 好了，开始看代码吧

#### 4.2.1 直接构造url无法通过验证

> 即使对于同一个公众号的历史消息/文章，wap_sid2和X-WECHAT-KEY都是每次变化的

**解决办法**

> 从微信客户端的一个页面开始，在Anyproxy中修改response，注入跳转页面的js脚本，实现自动收集数据。


## 工程模块

### 海马玩模拟器

使用WiFi，按住连接的WiFi进行配置，主要设置代理地址为本地主机地址，端口设为默认的8001。如果本机ip地址改变了了记得更新。

### 2018.04.16 微信更新

#### 崩溃1

> 微信会存储浏览过的文章，所以当再次浏览该文章时，不会请求文章内容，而会直接请求阅读数据.

暂时的解决办法，清除微信客户端的数据。

#### 解决思路

content和num分别请求mongodb.add
content: insert or update 

### 账号被封

> 具体不知道访问限制

- 每篇文章4-5s  （主要原因）
- 每个公众号20-30s    （感觉这个至少4s+）
- 每个batch 60-120s
- 每30个account暂停10min    （这个应该是主要原因）

## TODO

### 1 log功能

### 2 第二轮

### 3 公众号表，统计公众号数据


