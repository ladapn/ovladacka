from bluepy import btle

address = '00:13:AA:00:12:27'
service_uuid = btle.UUID('0000ffe0-0000-1000-8000-00805f9b34fb')
char_uuid = btle.UUID('0000ffe1-0000-1000-8000-00805f9b34fb')

p = btle.Peripheral( address )

svc = p.getServiceByUUID( service_uuid )
ch = svc.getCharacteristics( char_uuid )[0]
ch.write(b'B')
