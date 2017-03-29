# -*- coding: utf-8 -*-

import random
import operator
import time
from qqbot import QQBotSlot as qqbotslot, RunBot

REC_POINT = 3
DEF_POINT = 6
SKILL_COST = 10
acts = ["灵犀一指", "凤舞九天", "袖里乾坤", "摄魂大法", "横练十三太保", "金钟罩铁布衫", "流云飞袖", "铁砂掌", "如来神掌", "天残脚", "拈花指", "葵花宝典", "猴子偷桃", "神仙采葡萄", "挤奶龙抓手"]
point_dict = {}
ban_dict = {}
skill_dict = {}
qq_name = {}

# 通过群名片查找成员
def find_member(bot, g, name):
    return bot.List(bot.List('group', g.name)[0], 'name=' + name)[0]

# 通过QQ号查找成员
def find_qq(bot, g, qq):
    return bot.List(bot.List('group', g.name)[0], 'qq=' + qq)[0]

@qqbotslot
def onQQMessage(bot, contact, member, content):
    # 帮助
    if content == '-help':
        bot.SendTo(contact,
            (
                "道具帮助：'-help-skill'\n"
                "体力值查询：'-status'\n"
                "排行榜：'-rank'\n"
                "对决格式：'-fk at成员 分钟数'，分钟为大于0的整数且不超过发动者体力1.5倍\n"
                "胜利条件：发动攻击者命中率+怒气值大于等于100%。\n"
                "禁言惩罚：对决败者受到指定分钟数禁言。绝杀/自爆则为指定分钟数x3。\n"
                "体力值：初始体力值6。发动攻击者扣除分钟数对应体力值，若成功则双倍返还。防御者获得/失去分钟数对应体力值的一半。"
                "受绝杀后恢复体力值到3。\n"
                "绝杀奖励：取得人头者体力值增加10。"
            )
        )

    # 道具帮助
    elif content == '-help-skill':
        bot.SendTo(contact,
            (
                "购买道具：'-skill 道具编号' 消耗体力值" + str(SKILL_COST) + "\n"
                "1 - 圣盾：防御下一次攻击。\n"
                "2 - 致命一击：下一次攻击若成功，目标在自然解除前无法被救。"
            )
        )

    # 道具购买
    elif '-skill' in content:
        try:
            point_dict[member.qq]
        except:
            point_dict[member.qq] = DEF_POINT

        try:
            int(content[-1])
        except:
            bot.SendTo(contact, member.name + " 的购买格式错误，禁言1分钟。")
        try:
            skill_dict[member.qq]
        except:
            skill_dict[member.qq] = {}

        if int(content[-1]) == 1:
            skill_dict[member.qq][1] = True
            point_dict[member.qq] -= SKILL_COST
            bot.SendTo(contact, member.name + " 启用了道具 圣盾。")
        elif int(content[-1]) == 2:
            skill_dict[member.qq][2] = True
            point_dict[member.qq] -= SKILL_COST
            bot.SendTo(contact, member.name + " 启用了道具 致命一击。")
        else:
            bot.SendTo(contact, member.name + " 购买参数错误。")

        if point_dict[member.qq] < 0:
            # 自爆成功
            bot.SendTo(contact, member.name + " 自爆成功。")
            bot.GroupShut(contact, [member], t=60*SKILL_COST*3)
            point_dict[member.qq] = REC_POINT

    # 查询体力值
    elif content == '-status':
        try:
            point_dict[member.qq]
        except:
            point_dict[member.qq] = DEF_POINT
        bot.SendTo(contact, member.name + " 体力值: " + "{:.1f}".format(point_dict[member.qq]))

    # 排名
    elif content == '-rank':
        qq_name = {}
        for key in point_dict:
            try:
                qq_name[key] = find_qq(bot, contact, key).name
            except:
                pass
        sorted_point_dict = sorted(point_dict.items(), key=operator.itemgetter(1), reverse=True)
        s = "体力值排行"
        for t in sorted_point_dict:
            s += "\n" + qq_name[t[0]] + ":" + "{:.1f}".format(t[1])
        bot.SendTo(contact, s)

    # 对战
    elif '-fk' in content:

        # 尝试攻击机器人，被封10分钟
        if '@ME' in content:
            bot.SendTo(contact, member.name + " 你fk自己去吧。")
            bot.SendTo(contact, "YGY的机器人 使用了致命一击，命中率达到了100%！")
            bot.GroupShut(contact, [member], t=20*60)
            ban_dict[member.qq] = time.time() + 20*60
            return
        fk_from = member

        # 读取攻击信息
        l = content.split()
        if l[0] != '-fk' or l[1][0] != '@':
            bot.SendTo(contact, member.name + " 的攻击格式错误，禁言1分钟。")
            bot.GroupShut(contact, [member], t=1*60)
            return
        try:
            fk_minute = int(l[-1])
        except:
            bot.SendTo(contact, member.name + " 的攻击格式错误，禁言1分钟。")
            bot.GroupShut(contact, [member], t=1 * 60)
            return
        if fk_minute < 1:
            bot.SendTo(contact, member.name + " 的攻击格式错误，禁言1分钟。")
            bot.GroupShut(contact, [member], t=1 * 60)
            return
        l.pop()
        l.pop(0)
        fk_to_name = ' '.join(l)[1:]

        # 查找被攻击玩家
        try:
            fk_to = find_member(bot, contact, fk_to_name)
        except:
            bot.SendTo(contact, '发动攻击失败，正在喊YGY来抢修...')
            return

        # 初始化首次玩家体力值
        try:
            point_dict[fk_from.qq]
        except:
            point_dict[fk_from.qq] = DEF_POINT
        try:
            point_dict[fk_to.qq]
        except:
            point_dict[fk_to.qq] = DEF_POINT

        # 初始化道具
        try:
            skill_dict[fk_from.qq]
        except:
            skill_dict[fk_from.qq] = {}
        try:
            skill_dict[fk_to.qq]
        except:
            skill_dict[fk_to.qq] = {}

        # 体力值1.5倍限制
        if fk_minute > 1.5 * point_dict[fk_from.qq]:
            bot.SendTo(contact, fk_from.name + " 的攻击时间超过体力值1.5倍，禁言1分钟。")
            bot.GroupShut(contact, [fk_from], t=1*60)
            return

        # 被封玩家限制
        try:
            if ban_dict[fk_from.qq] > time.time():
                bot.SendTo(contact, fk_from.name + " 正处于禁言，无法发动攻击。")
                return
        except:
            ban_dict[fk_from.qq] = 0
        try:
            if ban_dict[fk_to.qq] > time.time():
                bot.SendTo(contact, fk_to.name + " 正处于致命一击的禁言，攻击非法，" + fk_from.name + " 禁言1分钟。")
                bot.GroupShut(contact, [fk_from], t=1*60)
                return
        except:
            ban_dict[fk_to.qq] = 0

        # 自己攻击自己限制
        if fk_from.qq == fk_to.qq:
            bot.SendTo(contact, fk_to.name + " 你这么喜欢自宫，那就给你双倍时间吧。")
            bot.GroupShut(contact, [fk_from], t=fk_minute*60*2)
            return

        # 攻击过程
        success_rate = random.random() * 100
        bot.SendTo(contact, fk_from.name + " 对 " + fk_to.name + " 发动" + str(fk_minute) + "分钟 "
                   + random.choice(acts) + " ，成功率" + "{0:.2f}%".format(success_rate) + "。")
        time.sleep(2)
        fk_rate = random.random() * 100
        bot.SendTo(contact, fk_from.name + " 的怒气值达到了" + "{0:.2f}%".format(fk_rate) + "！")
        time.sleep(1)

        # 判定
        try:
            skill_dict[fk_to.qq][1]
        except:
            skill_dict[fk_to.qq][1] = False
        try:
            skill_dict[fk_to.qq][2]
        except:
            skill_dict[fk_to.qq][2] = False
        try:
            skill_dict[fk_from.qq][1]
        except:
            skill_dict[fk_from.qq][1] = False
        try:
            skill_dict[fk_from.qq][2]
        except:
            skill_dict[fk_from.qq][2] = False

        if skill_dict[fk_to.qq][1] and success_rate + fk_rate >= 100:
            bot.SendTo(contact, fk_to.name + " 使用圣盾躲过了 " + fk_from.name + " 的攻击！")
        elif success_rate + fk_rate >= 100:
            # 攻击成功
            bot.SendTo(contact, fk_from.name + " 的攻击命中 " + fk_to.name + " ！获得体力值" + str(fk_minute) + "。")
            bot.GroupShut(contact, [fk_to], t=fk_minute*60)
            if skill_dict[fk_from.qq][2]:
                bot.SendTo(contact, fk_from.name + "的致命一击使得 " + fk_to.name + " 无法被解救！")
                ban_dict[fk_to.qq] = time.time() + fk_minute*60
            point_dict[fk_from.qq] += fk_minute
            point_dict[fk_to.qq] -= float(fk_minute) / 2.0
        else:
            # 攻击失败
            bot.SendTo(contact, fk_from.name + " 对 " + fk_to.name + " 的攻击失败，自己受到攻击并损失体力值 " + str(fk_minute) + "。")
            if skill_dict[fk_to.qq][1]:
                bot.SendTo(contact, fk_to.name + " 浪费了一个圣盾。")
            if skill_dict[fk_from.qq][2]:
                bot.SendTo(contact, fk_from.name + " 浪费了一个致命一击。")
            bot.GroupShut(contact, [fk_from], t=fk_minute*60)
            point_dict[fk_from.qq] -= fk_minute
            point_dict[fk_to.qq] += float(fk_minute) / 2.0

        # 道具清空
        skill_dict[fk_to.qq][1] = False
        skill_dict[fk_to.qq][2] = False
        skill_dict[fk_from.qq][1] = False
        skill_dict[fk_from.qq][2] = False

        # 绝杀判定
        bot.SendTo(contact, fk_from.name + " 剩余体力：" + "{:.1f}".format(point_dict[fk_from.qq]) + "\n"
                   + fk_to.name + " 剩余体力：" + "{:.1f}".format(point_dict[fk_to.qq]))
        if point_dict[fk_from.qq] < 0:
            # 自爆成功
            bot.SendTo(contact, fk_from.name + " 自爆成功。")
            bot.GroupShut(contact, [fk_from], t=fk_minute*60*3)
            #ban_dict[fk_from.qq] = time.time() + fk_minute*60*3
            point_dict[fk_from.qq] = 3
        if point_dict[fk_to.qq] < 0:
            # 绝杀成功
            bot.SendTo(contact, fk_from.name + " 对 " + fk_to.name + " 的绝杀成功，得到10点体力值奖励。")
            bot.GroupShut(contact, [fk_to], t=fk_minute*60*3)
            #ban_dict[fk_to.qq] = time.time() + fk_minute*60*3
            point_dict[fk_from.qq] += 10
            point_dict[fk_to.qq] = 3
        
    elif '是什么' in content:
        bot.SendTo(contact, "是sb")

    elif '@ME' in content:
        bot.SendTo(contact, "我是YGY的机器人！")

RunBot()