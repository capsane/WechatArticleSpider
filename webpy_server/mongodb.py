import pymongo


IP = "127.0.0.1"
PORT = 27017
DB = "wechat"


class MongoDB:
    def __init__(self, ip=IP, port=PORT, db=DB):
        super(MongoDB, self).__init__()
        print("new a MongoDB.")
        if not hasattr(self, '_db'):
            try:
                with pymongo.MongoClient(ip, port) as client:
                    self._db = client[db]
            except Exception as e:
                raise
            else:
                print("连接到数据库 %s" % db)

    def get_db(self):
        return self._db

    def find(self, collection, condition={}, limit=0, sort=[]):
        result = []
        if sort:
            result = self._db[collection].find(condition).limit(limit).sort(sort)
        else:
            result = self._db[collection].find(condition).limit(limit)
        return list(result)

    def findone(self, collection, condition):
        result = self._db[collection].find_one(condition)
        return result

    def add(self, collection, key_value):
        condition = {'biz': key_value['biz'], 'datetime': key_value['datetime'], 'idx': key_value['idx']}
        try:
            old = self.findone(collection, condition)
            if not old:
                # insert
                print("wechat insert...")
                self._db[collection].save(key_value)
            else:
                # update
                print("wechat update:")
                new = old.copy()
                del new['_id']
                self.delete(collection, old)
                if key_value['del_flag'] == 1:
                    print("update del_flag to 1...")
                    new['del_flag'] = 1
                else:
                    new['read_num'] = key_value['read_num']
                    new['like_num'] = key_value['like_num']
                self._db[collection].save(key_value)

        except Exception as e:
            print(e)
            return False
        else:
            return True

    def update(self, collection, old_value, new_value, multi=True):
        try:
            self._db[collection].update(old_value, {'$set': new_value}, multi=multi)
        except Exception as e:
            print(e)
            return False
        return True

    def delete(self, collection, condition={}):
        try:
            self._db[collection].remove(condition)
        except Exception as e:
            print(e)
            return False
        return True

    def set_unique_key(self, collection, key):
        try:
            self._db[collection].ensure_index(key, unique=True)
        except Exception as e:
            print(e)
            print("%s集合中%s存在重复的数据!!" % (collection, key))




