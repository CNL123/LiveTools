#修改line206,207的值，京东cookie中找
# python 3.6 云函数版本

import requests
import time
import json

"""
1、plantUuid 为自己的助力码，但是需要别人为自己助力
2、欢迎留下plantUuid互助
3. 抓包得cookies1中pt_key 和 pt_pin 内容，登录 https://bean.m.jd.com 点击签到并且出现签到日历后
 	
  返回抓包，搜索关键词 functionId=signBean 复制Cookie中的pt_key与pt_pin填入以下两个空白处
  cookies会过期,大约为一个月
"""

plantUuid = ["7pt22jcko7ljrbpeask7r6avre3h7wlwy7o5jii",
             "r7zdf2yfo4phlpel3nu4q63reu",
             "l4ex6vx6yynovld3unjojgbniop5fnqoyg5gegq"
             "fxnwpfvlyg2bjsayzhvfprz65mo5xypodtsgjnq",
             "e7lhibzb3zek2ssdsoyhpgn26va7nkkzj6ygely"]  # 填写别人的助力码

cookies1={
'pt_key': '',    #cookie参数填写
'pt_pin': '', 
}



# 微信推送
def pushWechat(key,desp):
    try:
        send_url='https://sc.ftqq.com/' + key + '.send'
        params = {
            'text': '种豆得豆签到' ,
            'desp': desp
        }
        requests.post(send_url,params=params)
    except Exception as e:
        print('server酱通知失败，异常代码：'+'\n'+str(e))


def functionTemplate(cookies, functionId, body):
    headers = {
        'Host': 'api.m.jd.com',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'User-Agent': 'JD4iPhone/167249 (iPhone;iOS 13.5.1;Scale/3.00)',
        'Accept-Language': 'zh-Hans-CN;q=1,en-CN;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': "application/x-www-form-urlencoded"
    }
    if "version" not in body:
        body["version"] = "9.0.0.1"
    body["monitor_source"] = "plant_app_plant_index"
    params = (
        ('functionId', functionId),
        ('body', json.dumps(body)),
        ('appid', 'ld'),
    )
    response = requests.get('https://api.m.jd.com/client.action',
                            headers=headers, params=params, cookies=cookies)
    return json.loads(response.text)


def takeTask(cookies, taskList):
    # for i in taskList:
    #     print(i,"\n")
    time.sleep(2)
    taskResult = functionTemplate(cookies, "receiveNutrientsTask", {
        "monitor_refer": "receiveNutrientsTask", "awardType": "7"})  # 金融双签 额外
    print(taskResult)
    time.sleep(2)
    taskResult = functionTemplate(cookies, "receiveNutrientsTask", {
        "monitor_refer": "plant_receiveNutrientsTask", "awardType": "4"})  # 逛逛会场
    print(taskResult)
    for i in taskList:

        if i["dailyTimes"] == 1 and i["gainedNum"] == "0" and i["taskType"] != 8:
            print(i)
            taskResult = functionTemplate(cookies, "receiveNutrientsTask", {
                "monitor_refer": "receiveNutrientsTask", "awardType": str(i["taskType"])})
            print(taskResult)
            time.sleep(2)
        if i["taskType"] == 7 and i["isFinished"] == 0:  # 金融双签 有时候不出现在taskList
            taskResult = functionTemplate(cookies, "receiveNutrientsTask", {
                "monitor_refer": "receiveNutrientsTask", "awardType": str(i["taskType"])})
            print(taskResult)
            time.sleep(2)
        if i["taskType"] == 3 and i["isFinished"] == 0:
            print("浏览店铺")
            N = int(i["totalNum"]) - int(i["gainedNum"])
            plant_shopList = functionTemplate(cookies, "shopTaskList", {
                "monitor_refer": "plant_receiveNutrients"})["data"]
            goodShopList = [
                i for i in plant_shopList["goodShopList"] if i["taskState"] == "2"]
            moreShopList = [
                i for i in plant_shopList["moreShopList"] if i["taskState"] == "2"]
            shopList = goodShopList + moreShopList
            for shop in shopList:
                shopTaskId = shop["shopTaskId"]
                shopId = shop["shopId"]
                result = functionTemplate(cookies, "shopNutrientsTask", {
                    "monitor_refer": "plant_shopNutrientsTask", "shopId": str(shopId), "shopTaskId": str(shopTaskId)})
                print(result)
                if "data" in result:
                    if result["data"]["nutrState"] == "1":
                        N -= 1
                if N == 0:
                    break
                time.sleep(1)
        if i["taskType"] == 10 and i["isFinished"] == 0:
            print("关注频道")
            N = int(i["totalNum"]) - int(i["gainedNum"])
            plant_ChannelList = functionTemplate(
                cookies, "plantChannelTaskList", {})["data"]
            goodChannelList = [
                i for i in plant_ChannelList["goodChannelList"] if i["taskState"] == "2"]
            normalChannelList = [
                i for i in plant_ChannelList["normalChannelList"] if i["taskState"] == "2"]
            channelList = goodChannelList + normalChannelList

            for channel in channelList:
                result = functionTemplate(cookies, "plantChannelNutrientsTask",
                                          {"channelTaskId": channel["channelTaskId"], "channelId": channel["channelId"]
                                           })
                print(result)
                if "data" in result:
                    if result["data"]["nutrState"] == "1":
                        N -= 1
                if N == 0:
                    break
                time.sleep(1)
        if i["taskType"] == 5 and i["isFinished"] == 0:
            print("挑选商品")
            N = int(i["totalNum"]) - int(i["gainedNum"])
            productInfoList = functionTemplate(cookies, "productTaskList", {
                "monitor_refer": "plant_productTaskList"})["data"]["productInfoList"]
            productList = sum(productInfoList, [])
            productList = list(
                filter(lambda i: i["taskState"] == "2", productList))

            for product in productList:
                result = functionTemplate(cookies, "productNutrientsTask", {
                    "productTaskId": product["productTaskId"], "skuId": product["skuId"],
                    "monitor_refer": "plant_productNutrientsTask"})
                print(result)
                if "data" in result:
                    if result["data"]["nutrState"] == "1":
                        N -= 1
                if N == 0:
                    break
                time.sleep(1)


def _help(cookies, plantUuid):
    for i in plantUuid:
        functionTemplate(cookies, "plantBeanIndex", {
            "plantUuid": i, "followType": "1", "wxHeadImgUrl": "", "shareUuid": "", })


def steal(cookies, roundId):
    print("\n【偷取营养液】\n默认对方有3个才会偷取\n不足自动跳过 ")
    pageNum = 1
    while ("data" in functionTemplate(cookies, "plantFriendList", {"pageNum": str(pageNum)})):
        time.sleep(2)
        result = functionTemplate(cookies, "plantFriendList", {
            "pageNum": str(pageNum)})
        # print(result)
        if "tips" in result["data"]:
            print("今日已达上限")
            # exit()
            return
        # exit()
        stealList = [i for i in result["data"]
        ["friendInfoList"] if "nutrCount" in i]

        for i in stealList:

            if int(i["nutrCount"]) == 3:  # 为3时才会偷取
                print(i)
                print(functionTemplate(cookies, "collectUserNutr", {
                    "paradiseUuid": i["paradiseUuid"], "roundId": roundId}))
                time.sleep(2)


def getReward(cookies, status):
    print("\n[收获状况]")
    if status == "5":
        data = functionTemplate(
            cookies, "receivedBean", {"roundId": lastRoundId})["data"]
        print(f"""{data["growth"]}成长值兑换{data["awardBean"]}京豆""")
    if status == "6":
        print("您已领奖，去京豆明细页看看")


def water(cookies):
    print("\n[浇水ing]")
    result = functionTemplate(cookies, "cultureBean", {
        "roundId": currentRoundId, "monitor_refer": "plant_index"})
    if "errorMessage" in result:
        print(result["errorMessage"])
        return


def egg(cookies):
    try:
        msg = ''
        print("\n[天天扭蛋]")
        restLotteryNum = functionTemplate(cookies, "plantEggLotteryIndex", {})[
            "data"]["restLotteryNum"]
        if restLotteryNum == 0:
            print(">>>暂无扭蛋")
            msg += ">>>暂无扭蛋"
        for i in range(restLotteryNum):
            print(">>>扭蛋 ", i + 1)
            functionTemplate(cookies, "plantEggDoLottery", {})
            msg += ">>>扭蛋"
    except Exception as e:
        print('二签失败，异常代码：' + '\n' + str(e))
        msg += '\n二签失败，异常代码：' + '\n' + str(e)

    return msg

def waterWheel(cookies):
    print("\n[水车生产(6-21)]")
    result = functionTemplate(cookies, "receiveNutrients", {
        "roundId": currentRoundId, "monitor_refer": "plant_receiveNutrients"})
    if "errorMessage" in result:
        print(result["errorMessage"])
        return






def valid(cookies1):
    headers = {
        'Host': 'api.m.jd.com',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'User-Agent': 'jdapp;iPhone;8.5.5;13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1',
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    params = (
        ('functionId', 'plantBeanIndex'),
        ('body', json.dumps(
            {"monitor_source": "plant_m_plant_index", "version": "8.4.0.0"})),
        ('appid', 'ld'),
    )
    response = requests.get('https://api.m.jd.com/client.action',
                            headers=headers, params=params, cookies=cookies1)
    if response.json()["code"] == "3":
        print(f"""## {cookies["pt_pin"]}: cookie过期""")
        return False
    return True

# def get_cookies():
    # return [i for i in cookiesLists if valid(i)] #多账户



plantBeanIndex = functionTemplate(cookies1, "plantBeanIndex", {})

print(
        f"""【{plantBeanIndex["data"]["plantUserInfo"]["plantNickName"]}】\n""")
print(
        f"""我的助力码: {plantBeanIndex["data"]["jwordShareInfo"]["shareUrl"].split("=")[-1]}\n""")
print(1)
_help(cookies1, plantUuid)
print(2)
roundList = plantBeanIndex["data"]["roundList"]
lastRoundId = roundList[0]["roundId"]  # 上期id
currentRoundId = roundList[1]["roundId"]  # 本期id


    # print("\nEND\n")
    # print("##" * 30)

def main():
    taskList = plantBeanIndex["data"]["taskList"]  # 任务列表
    takeTask(cookies1, taskList)  # 执行每日任务
    print("     任务   进度")
    for i in functionTemplate(cookies1, "plantBeanIndex", {})["data"]["taskList"]:
        print(
            f"""[{i["taskName"]}]  {i["gainedNum"]}/{i["totalNum"]}   {i["isFinished"]} """)
        msg = f"""[{i["taskName"]}]  {i["gainedNum"]}/{i["totalNum"]}   {i["isFinished"]} """

    egg(cookies1)
    waterWheel(cookies1)
    steal(cookies1, currentRoundId)
    water(cookies1)
    getReward(cookies1, roundList[0]["awardState"])
    pushWechat(server_key,msg)

def main_handler(event, context):
    return main()

if __name__ == '__main__':
    main()
