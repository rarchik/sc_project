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

vk = vk_api.VkApi(token="")



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

worksheet = sh.worksheet("klass")
c1 = worksheet.col_values(1)
c2 = worksheet.col_values(2)
kl = {}

for i in range(len(c1)):
	kl.update([(c1[i], c2[i])])

keydoards = {}

numb = VkKeyboard(one_time=True)

numb.add_button('5', color=VkKeyboardColor.PRIMARY)
numb.add_button('6', color=VkKeyboardColor.PRIMARY)
numb.add_button('7', color=VkKeyboardColor.PRIMARY)
numb.add_line()
numb.add_button('8', color=VkKeyboardColor.POSITIVE)
numb.add_button('9', color=VkKeyboardColor.POSITIVE)
numb.add_button('10', color=VkKeyboardColor.POSITIVE)
numb.add_line()
numb.add_button('11', color=VkKeyboardColor.PRIMARY)

numb = numb.get_keyboard()
j = []
p = 0
for i in range(5,12):
	for y in c1:
		if str(i) in y:
			j.append(y)

	key = VkKeyboard(one_time=True)

	for y in j:
		if p == 3:
			p = 0
			key.add_line()
			key.add_button(y, color=VkKeyboardColor.PRIMARY)
		else:
			key.add_button(y, color=VkKeyboardColor.PRIMARY)
		p += 1

	j = []
	p = 0
	keydoards.update([(i, key.get_keyboard())])

ty = 0
tr = 0
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

				cur.execute("INSERT INTO `uch`(`num`, `id`, `name`, `klas`, `send`, 'stat') VALUES ({}, {}, '{}', '{}', 0, 0)".format(num, id, h[0]['first_name']+' '+h[0]['last_name'], '-'))
				con.commit()

				vk.method("messages.send", {"peer_id": id, "message": 'Выбери номер класса, в котором ты учишся:', 'keyboard': numb, 'random_id':0})

			else:
				print(value.strftime('%Y-%m-%d %H:%M:%S'),'-',body,' - ',id, ' - ',h[0]['first_name']+' '+h[0]['last_name'])
				cur.execute("SELECT * FROM `uch` WHERE `id` = "+str(id))
				baz = cur.fetchall()[0]
				if baz['klas'] not in kl.values():
					try:
						if body in kl.keys():
							cur.execute("UPDATE `uch` SET `klas`= '{}', `stat` = 2 WHERE `id` = {}".format(kl[body], id))
							con.commit()

							cur.execute("SELECT `send` FROM `uch` WHERE `id` = {}".format(id))
							if cur.fetchall()[0]['send'] == 0:
								vk.method("messages.send", {"peer_id": id, "message": 'Отлично! Теперь я могу оповещать тебя о звонках👍', 'keyboard': keyboard3, 'random_id':0})
							else: 
								vk.method("messages.send", {"peer_id": id, "message": 'Отлично! Теперь я могу оповещать тебя о звонках👍', 'keyboard': keyboard4, 'random_id':0})
					
						elif baz['stat'] == 0 and int(body) in keydoards.keys():
							cur.execute("UPDATE `uch` SET `stat` = 1 WHERE `id` = {}".format(id))
							con.commit()
							vk.method("messages.send", {"peer_id": id, "message": 'Выберай свой класс.', 'keyboard': keydoards[int(body)], 'random_id':0})
						else:
							vk.method("messages.send", {"peer_id": id, "message": 'Пользуйся кнопками.', 'keyboard': numb, 'random_id': 0})

					except: 
						vk.method("messages.send", {"peer_id": id, "message": 'Пользуйся кнопками.', 'keyboard': numb, 'random_id': 0})
					# elif body == '--->':
					# 	vk.method("messages.send", {"peer_id": id, "message": 'Следующая страница.', 'keyboard': keyboard2, 'random_id': 0})

					# elif body == '<---':
					# 	vk.method("messages.send", {"peer_id": id, "message": 'Предидущая страница.', 'keyboard': keyboard1, 'random_id': 0})

					
				else:
					cur.execute("SELECT `send` FROM `uch` WHERE `id` = {}".format(id))
					if cur.fetchall()[0]['send'] == 0:
						if body == 'Сменить класс.':
							cur.execute("UPDATE `uch` SET `klas`= '{}', `stat`= 0 WHERE `id` = {}".format('-', id))
							con.commit()

							vk.method("messages.send", {"peer_id": id, "message": 'Выберай новый класс.', 'keyboard': numb, 'random_id':0})

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
							cur.execute("UPDATE `uch` SET `klas`= '{}', `stat`= 0 WHERE `id` = {}".format('-', id))
							con.commit()

							vk.method("messages.send", {"peer_id": id, "message": 'Выберай новый класс.', 'keyboard': numb, 'random_id':0})

						elif body == 'Расписание(на доработке).':
							vk.method("messages.send", {"peer_id": id, "message": 'На доработке...', 'keyboard': keyboard4, 'random_id':0})

						elif body == 'Включить уведомления.':
							cur.execute("UPDATE `uch` SET `send`= 0 WHERE `id` = {}".format(id))
							con.commit()
							vk.method("messages.send", {"peer_id": id, "message": 'Уведомления включены.', 'keyboard': keyboard3, 'random_id':0})

						else:
							vk.method("messages.send", {"peer_id": id, "message": 'Пользуйся кнопками.', 'keyboard': keyboard4, 'random_id':0})

		# обновляю базу звонков
		if ty == 0:
			worksheet = sh.worksheet("zvon")
			s = worksheet.col_values(1)[1:]
			print('zvon base update')

		ty += 1
		if ty > 60:
			ty = 0
		

		# обновляю базу классов
		if tr == 0:
			worksheet = sh.worksheet("klass")
			c1 = worksheet.col_values(1)
			c2 = worksheet.col_values(2)
			kl = {}

			for i in range(len(c1)):
				kl.update([(c1[i], c2[i])])

			keydoards = {}

			numb = VkKeyboard(one_time=True)

			numb.add_button('5', color=VkKeyboardColor.PRIMARY)
			numb.add_button('6', color=VkKeyboardColor.PRIMARY)
			numb.add_button('7', color=VkKeyboardColor.PRIMARY)
			numb.add_line()
			numb.add_button('8', color=VkKeyboardColor.POSITIVE)
			numb.add_button('9', color=VkKeyboardColor.POSITIVE)
			numb.add_button('10', color=VkKeyboardColor.POSITIVE)
			numb.add_line()
			numb.add_button('11', color=VkKeyboardColor.PRIMARY)

			numb = numb.get_keyboard()
			j = []
			p = 0
			for i in range(5,12):
				for y in c1:
					if str(i) in y:
						j.append(y)

				key = VkKeyboard(one_time=True)

				for y in j:
					if p == 3:
						p = 0
						key.add_line()
						key.add_button(y, color=VkKeyboardColor.PRIMARY)
					else:
						key.add_button(y, color=VkKeyboardColor.PRIMARY)
					p += 1

				j = []
				p = 0
				keydoards.update([(i, key.get_keyboard())])
			print('klass base update')
		tr += 1
		if tr > 120:
			tr = 0




		value = datetime.datetime.fromtimestamp(time.time())
		d = value.strftime('%H:%M')

		if d[0] == '0':
			d = d[1:]
		
		print(d)
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