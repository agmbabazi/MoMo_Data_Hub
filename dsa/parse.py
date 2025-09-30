import xml.etree.ElementTree as ET
from typing import Any

def get_messages(data):
    """This function gets all messages"""
    all_data = data.findall("sms")
    if not all_data:
        return []
    return [node.attrib["body"] for node in all_data]

class TransactionMessages:
    def __init__(self, messages: Any):
        self.__all_messages = messages

    def check_messages(self, messages) -> list[str]:
        """This function checks if message is available"""
        if not messages:
            return None
        self.__all_messages = messages
        return self.__all_messages

    def get_received(self, messages) -> list[str]:
        """This function gets all income messages from Momo to Momo"""
        if not self.check_messages(messages):
            return []
        return [
            message for message in self.__all_messages
            if message.startswith("You have received")
        ]

    def get_momo_payment(self, messages) -> list[str]:
            if not self.check_messages(messages):
            return []
        return [
            message for message in self.__all_messages
            if re.search(r"your payment of", message, re.I)
        ]

    def get_bank_deposit(self, messages) -> list[str]:
            if not self.check_messages(messages):
            return []
        return [
            message for message in self.__all_messages
            if message.startswith("*113*R*A bank deposit of")
        ]

    def get_withdraw(self, messages) -> list[str]:
            if not self.check_messages(messages):
            return []
        return [
            message for message in self.__all_messages
            if re.search("withdrawn", message, re.I)
        ]

    def get_transfer(self, messages) -> list[str]:
            if not self.check_messages(messages):
            return []
        return [
            message for message in self.__all_messages
            if re.search(r"transferred to", message, re.I)
        ]

if __name__ == "__main__":
    momo_data = ET.parse(r"E:\MoMo_Data_Hub\data\modified_sms_v2.xml")
    all_messages = get_messages(data=momo_data.getroot())
    user_transaction = TransactionMessages(messages=all_messages)

    for pay in user_transaction.get_momo_income(messages=all_messages):
        print(f"{pay}\n")
