# -*- coding: utf-8 -*-
#!/usr/bin/python3


import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import datetime
import time
import pymysql
import pymysql.cursors
import gspread

con = pymysql.connect(host='localhost',
        user='root',
        password='usbw',
        db='prbd',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor)

cur = con.cursor()

gc = gspread.service_account(filename='mypython-290810-dd40e29bd1bb.json')

sh = gc.open("sc pro")

vk = vk_api.VkApi(token="3e717cbe0e45952a041a8d8df40a5d7232801a2ac114e5f3714b605d39d0ae94f42862d9c205e6aed9f52")

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

keyboard4 = VkKeyboard(one_time=True)

keyboard4.add_button('Сменить класс.', color=VkKeyboardColor.POSITIVE)
keyboard4.add_button('Расписание(на доработке).', color=VkKeyboardColor.PRIMARY)
keyboard4.add_line()
keyboard4.add_button('Включить уведомления.', color=VkKeyboardColor.POSITIVE)

keyboard4 = keyboard4.get_keyboard()

kl = {'5Д':'5d', '5Л':'5l', '5К':'5k',
	  '6К':'6k', '6Л':'6l',
	  '7К':'7k', '7Л':'7l',
	  '8К':'8k', '8Л':'8l',
	  '9К':'9k', '9Л':'9l',
	  '10Л':'10l',
	  '11Л':'11l'}

ty = 0
sends = []

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

				cur.execute("INSERT INTO `uch`(`num`, `id`, `name`, `klas`, `send`) VALUES ({}, {}, '{}', '{}', 0)".format(num, id, h[0]['first_name']+' '+h[0]['last_name'], '-'))
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
						vk.method("messages.send", {"peer_id": id, "message": 'Следующая страница.', 'keyboard': keyboard2, 'random_id': 0})

					elif body == '<---':
						vk.method("messages.send", {"peer_id": id, "message": 'Предидущая страница.', 'keyboard': keyboard1, 'random_id': 0})

					else:
						vk.method("messages.send", {"peer_id": id, "message": 'Пользуйся кнопками.', 'keyboard': keyboard1, 'random_id': 0})
				else:
					cur.execute("SELECT `send` FROM `uch` WHERE `id` = {}".format(id))
					if cur.fetchall()[0]['send'] == 0:
						if body == 'Сменить класс.':
							cur.execute("UPDATE `uch` SET `klas`= '{}' WHERE `id` = {}".format('-', id))
							con.commit()

							vk.method("messages.send", {"peer_id": id, "message": 'Выберай новый класс.', 'keyboard': keyboard1, 'random_id': 0})

						elif body == 'Расписание(на доработке).':
							vk.method("messages.send", {"peer_id": id, "message": 'На доработке...', 'keyboard': keyboard3, 'random_id': 0})

						elif body == 'Отключить уведомления.':
							cur.execute("UPDATE `uch` SET `send`= 1 WHERE `id` = {}".format(id))
							con.commit()
							vk.method("messages.send", {"peer_id": id, "message": 'Уведомления выключены.', 'keyboard': keyboard4, 'random_id': 0})

						else:
							vk.method("messages.send", {"peer_id": id, "message": 'Пользуйся кнопками.', 'keyboard': keyboard3, 'random_id':0})

					else:
						if body == 'Сменить класс.':
							cur.execute("UPDATE `uch` SET `klas`= '{}' WHERE `id` = {}".format('-', id))
							con.commit()

							vk.method("messages.send", {"peer_id": id, "message": 'Выберай новый класс.', 'keyboard': keyboard1, 'random_id':0})

						elif body == 'Расписание(на доработке).':
							vk.method("messages.send", {"peer_id": id, "message": 'На доработке...', 'keyboard': keyboard4, 'random_id':0})

						elif body == 'Включить уведомления.':
							cur.execute("UPDATE `uch` SET `send`= 0 WHERE `id` = {}".format(id))
							con.commit()
							vk.method("messages.send", {"peer_id": id, "message": 'Уведомления включены.', 'keyboard': keyboard3, 'random_id':0})

						else:
							vk.method("messages.send", {"peer_id": id, "message": 'Пользуйся кнопками.', 'keyboard': keyboard4, 'random_id':0})

		if ty == 0:
			worksheet = sh.worksheet("zvon")
			s = worksheet.col_values(1)[1:]

		ty += 1
		if ty > 30:
			ty = 0
			
		value = datetime.datetime.fromtimestamp(time.time())
		d = value.strftime('%H:%M')

		if d[0] == '0':
			d = d[1:]
		
		print(ty, d)
		ans = {}

		if (d in s) and (d not in sends):
			worksheet = sh.worksheet("zvon")
			a = worksheet.findall(d)[0] 
			if worksheet.cell(a.row, 2).value != 1:
				for i in kl.values():
					worksheet = sh.worksheet(i)
					a = worksheet.findall(d)
					# print(a, i)
					if a != []:
						a = a[0]

						if a.col == 2:
							a = 'Начался {} урок.'.format(worksheet.cell(a.row, 1).value)
							ans.update([(i, a)])

						elif a.col == 3:
							a = 'Закончился {} урок.'.format(worksheet.cell(a.row, 1).value)
							ans.update([(i, a)])

				print(ans)

				for i in ans.keys():
					cur.execute("SELECT `id` FROM `uch` WHERE `klas` = '{}' and `send` = 0".format(i))

					for t in cur.fetchall():
						vk.method("messages.send", {"peer_id": t['id'], "message": ans[i], 'keyboard': keyboard3, 'random_id':0})

				worksheet = sh.worksheet("zvon")
				a = worksheet.findall(d)[0]
				sends.append(d)

				worksheet.update_cell(a.row, 2, 1)
				worksheet.format("B"+str(a.row), {
				"backgroundColor": {
					"red": 0.0,
					"green": 100.0,
					"blue": 0.0
				}})
				
			else:
				pass

		elif d == '18:00':
			f = []
			sends = []
			for i in range(len(s)):
				f.append([0])
			worksheet.update('B2:B', f)
			worksheet.format("B2:B36", {
			"backgroundColor": {
				"red": 100.0,
				"green": 0.0,
				"blue": 0.0
			}})
					

		else:
			time.sleep(0.5)

	except Exception as err:
		print(err)
		vk.method("messages.send", {"peer_id": 226178635, "message": err, 'random_id':0})

# d = value.strftime('%w')