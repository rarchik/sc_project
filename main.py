# -*- coding: utf-8 -*-
#!/usr/bin/python3


import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import datetime
import time
import pymysql
import pymysql.cursors

con = pymysql.connect(host='localhost',
        user='root',
        password='usbw',
        db='prbd',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor)

cur = con.cursor()

vk = vk_api.VkApi(token="")

keyboard1 = VkKeyboard(one_time=True)

keyboard1.add_button('5Д', color=VkKeyboardColor.PRIMARY)
keyboard1.add_button('5К', color=VkKeyboardColor.PRIMARY)
keyboard1.add_button('5Л', color=VkKeyboardColor.PRIMARY)
keyboard1.add_line()
keyboard1.add_button('6К', color=VkKeyboardColor.NEGATIVE )
keyboard1.add_button('6Л', color=VkKeyboardColor.NEGATIVE )
keyboard1.add_line()
keyboard1.add_button('7К', color=VkKeyboardColor.POSITIVE)
keyboard1.add_button('7Л', color=VkKeyboardColor.POSITIVE)
keyboard1.add_line()
keyboard1.add_button('8К', color=VkKeyboardColor.NEGATIVE )
keyboard1.add_button('8Л', color=VkKeyboardColor.NEGATIVE )
keyboard1.add_line()
keyboard1.add_button('--->', color=VkKeyboardColor.PRIMARY)

keyboard1 = keyboard1.get_keyboard()

keyboard2 = VkKeyboard(one_time=True)

keyboard2.add_button('9К', color=VkKeyboardColor.PRIMARY)
keyboard2.add_button('9Л', color=VkKeyboardColor.PRIMARY)
keyboard2.add_line()
keyboard2.add_button('10Л', color=VkKeyboardColor.POSITIVE)
keyboard2.add_line()
keyboard2.add_button('11Л', color=VkKeyboardColor.PRIMARY)
keyboard2.add_line()
keyboard2.add_button('<---', color=VkKeyboardColor.PRIMARY)

keyboard2 = keyboard2.get_keyboard()

keyboard3 = VkKeyboard(one_time=True)

keyboard3.add_button('Сменить класс.', color=VkKeyboardColor.POSITIVE)
keyboard3.add_button('Расписание(на доработке).', color=VkKeyboardColor.PRIMARY)
keyboard3.add_line()
keyboard3.add_button('Отключить уведомления.', color=VkKeyboardColor.NEGATIVE)

keyboard3 = keyboard3.get_keyboard()

kl = {'5Д':'5d', '5Л':'5l', '5К':'5k',
	  '6К':'6k', '6Л':'6l',
	  '7К':'7k', '7Л':'7l',
	  '8К':'8k', '8Л':'8l',
	  '9К':'9k', '9Л':'9l',
	  '10Л':'10l',
	  '11Л':'11l'}

while True:
	try:
		messages = vk.method("messages.getConversations", {"offset": 0, "count": 20,"filter":"unread"})

		if messages["count"] >= 1:
			messages = vk.method("messages.getConversations", {"offset": 0, "count": 20,"filter":"unread"})
			id = messages["items"][0]["last_message"]["from_id"]
			body = messages["items"][0]["last_message"]["text"]
			h = vk.method('users.get',{'user_ids':id,'name_case':'Nom'})

			timestamp = time.time()
			value = datetime.datetime.fromtimestamp(timestamp)

			cur.execute("SELECT * FROM `uch` WHERE `id` = "+str(id))
			if cur.execute("SELECT * FROM `uch` WHERE `id` = "+str(id)) == 0:
				print('New in base')

				cur.execute("SELECT `num` FROM `uch`")
				num = cur.fetchall()
				num = num[-1]['num'] + 1

				cur.execute("INSERT INTO `uch`(`num`, `id`, `name`, `klas`) VALUES ({}, {}, '{}', '{}')".format(num, id, h[0]['first_name']+' '+h[0]['last_name'], '-'))
				con.commit()

				vk.method("messages.send", {"peer_id": id, "message": 'Выбери класс, в котором ты учишся:', 'keyboard': keyboard1, 'random_id':0})
			
			else:
				print(value.strftime('%Y-%m-%d %H:%M:%S'),'-',body,' - ',id, ' - ',h[0]['first_name']+' '+h[0]['last_name'])
				cur.execute("SELECT * FROM `uch` WHERE `id` = "+str(id))
				if cur.fetchall()[0]['klas'] == '-':
					if body in kl.keys():
						cur.execute("UPDATE `uch` SET `klas`= '{}' WHERE `id` = {}".format(kl[body], id))
						con.commit()

						vk.method("messages.send", {"peer_id": id, "message": 'Отлично! Теперь я могу оповещать тебя о звонках👍', 'keyboard': keyboard3, 'random_id':0})
					
					elif body == '--->':
						vk.method("messages.send", {"peer_id": id, "message": 'Следующая страница.', 'keyboard': keyboard2, 'random_id':0})

					elif body == '<---':
						vk.method("messages.send", {"peer_id": id, "message": 'Предидущая страница.', 'keyboard': keyboard1, 'random_id':0})

					else:
						vk.method("messages.send", {"peer_id": id, "message": 'Пользуйся кнопками.', 'keyboard': keyboard1, 'random_id':0})
				else:
					if body == 'Сменить класс.':
						cur.execute("UPDATE `uch` SET `klas`= '{}' WHERE `id` = {}".format('-', id))
						con.commit()

						vk.method("messages.send", {"peer_id": id, "message": 'Выберай новый класс.', 'keyboard': keyboard1, 'random_id':0})

					elif body == 'Расписание(на доработке).':
						vk.method("messages.send", {"peer_id": id, "message": 'На доработке...', 'keyboard': keyboard3, 'random_id':0})

					elif body == 'Отключить уведомления.':
						# SELECT `id` FROM `uch` WHERE `klas` = '5k' and `send` = 0
						cur.execute("UPDATE `uch` SET `send`= 1 WHERE `id` = {}".format(id))
						con.commit()

					else:
						vk.method("messages.send", {"peer_id": id, "message": 'Пользуйся кнопками.', 'keyboard': keyboard3, 'random_id':0})

		s = []
		cur.execute("SELECT `time` FROM `zvon`")
		for i in cur.fetchall():
			s.append(i['time'])

		value = datetime.datetime.fromtimestamp(time.time())
		d = value.strftime('%H:%M')
		print(d)
		ans = {}

		if d in s:
			print("SELECT `send` FROM `zvon` WHERE `time` = '{}'".format(d))

			cur.execute("SELECT `send` FROM `zvon` WHERE `time` = '{}'".format(d))
			if cur.fetchall()[0]['send'] != 1:
				for i in kl.values():
					if cur.execute("SELECT * FROM `{}` WHERE `start` = '{}'".format(i, d)) != 0:
						a = 'Начался {} урок.'.format(cur.fetchall()[0]['num'])
						ans.update([(i, a)])
					elif cur.execute("SELECT * FROM `{}` WHERE `end` = '{}'".format(i, d)) != 0:
						a = 'Закончился {} урок.'.format(cur.fetchall()[0]['num'])
						ans.update([(i, a)])
				
				for i in ans.keys():
					cur.execute("SELECT `id` FROM `uch` WHERE `klas` = '{}' and `send` = 0".format(i))

					for t in cur.fetchall():
						vk.method("messages.send", {"peer_id": t['id'], "message": ans[i], 'keyboard': keyboard3, 'random_id':0})

				cur.execute("UPDATE `zvon` SET `send`= 1 WHERE `time` = '{}'".format(d))
				con.commit()
			else:
				pass

		elif d == '18:00':
			for i in s:
				cur.execute("UPDATE `zvon` SET `send`= 0 WHERE `time` = '{}'".format(i))
				con.commit()

		else:
			time.sleep(0.5)

	except Exception as err:
		print(err)
		vk.method("messages.send", {"peer_id": 226178635, "message": err, 'random_id':0})


