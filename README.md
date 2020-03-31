00:13:AA:00:12:27

Primary Service (Handle 0xcf71)
	/org/bluez/hci0/dev_00_13_AA_00_12_27/service0023
	0000ffe0-0000-1000-8000-00805f9b34fb
	Unknown

Characteristic (Handle 0xcf71)
	/org/bluez/hci0/dev_00_13_AA_00_12_27/service0023/char0024
	0000ffe1-0000-1000-8000-00805f9b34fb
	Unknown

bluepy's handling of incomming notifications is not much asynchronous, it just 
checks for notification during any bluepy call (read, write, waitfornotifications...)


---

connect 00:13:AA:00:12:27
menu gatt
select-attribute /org/bluez/hci0/dev_00_13_AA_00_12_27/service0023/char0024
write 64




