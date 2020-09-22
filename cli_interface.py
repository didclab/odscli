from aioconsole import ainput
class ODSCLI:
    def __init__(self):
        self.commands = {}

    def addCommand(self,name,command):
        if name in self.commands:
            raise ValueError('Command already registered')
        self.commands[name] = command 

    async def run():
        while True:
            userInput = await ainput(prompt='ODS-CLI >> ')
            if not userInput:
                continue
            if userInput == 'test':
                print("this test works")
            elif userInput == 'exit':
                return
            elif userInput == 'hello':
                print("Hey There!")
            else:
                print('not the key word test')
