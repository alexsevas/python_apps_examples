# pip install pyusb


import usb.core
dev = usb.core.find(idVendor=0x046d, idProduct=0xc534)  # Указать VID и PID
if dev:
    print("Устройство найдено!")
