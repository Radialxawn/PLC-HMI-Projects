list_count = 100
update_step = 5
string_length = 32

for i in range(list_count):
	print('GetData(name[0], "PLC", "Application.M.hmi.prf_name[%d]", %d)' % (i, string_length))
	print('SetData(name[0], "Self", LW, %d, %d)' % (200 + i * string_length, string_length))
	if i % update_step == 0:
		print('SetData(update, "Self", "list_update", 1)')
		print('list_progress = %d' % int(i * 100 / list_count))
		print('SetData(list_progress, "Self", "list_progress", 1)')