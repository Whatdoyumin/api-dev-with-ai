raw = """
<users>
    <user>
        <id>1</id>
        <name>김민석</name>
        <profile>
            <email>kim@email.com</email>
            <phone>010-1234-5678</phone>
        </profile>
    </user>
    <user>
        <id>2</id>
        <name>홍길동</name>
        <profile>
            <email>hong@email.com</email>
            <phone>010-9876-5432</phone>
        </profile>
    </user>
</users>
"""

import xml.etree.ElementTree as ET

try:
    root = ET.fromstring(raw)
    for e in root.findall("user"):
        print(e.findtext("id", "default"))
        print(e.findtext("name", "default"))
        print(e.findtext("profile/email", "default"))
        print(e.findtext("profile/phone", "default"))

except Exception as e:
    print("XML 파싱 오류")