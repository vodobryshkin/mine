from javascript import require, On
from time import sleep
import os

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')


class MineBot:
    def __init__(self, username, server, version):
        self.username = username
        self.version = version
        self.server = server
        self.running = False

        self.host, self.port = server.split(':')
        self.port = int(self.port)

        self.bot = mineflayer.createBot({
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'version': self.version
        })

        self.bot.loadPlugin(pathfinder.pathfinder)

    def run(self):
        self.running = True

        RANGE_GOAL = 1
        FISHING_INTERVAL = 2

        GoalFollow = pathfinder.goals.GoalFollow
        GoalBlock = pathfinder.goals.GoalBlock

        @On(self.bot, 'spawn')
        def spawn(*args1):
            mc_data = require('minecraft-data')(self.bot.version)
            movements = pathfinder.Movements(self.bot, mc_data)

            @On(self.bot, 'chat')
            def message_handler(this, user, message, *args2):
                if user != self.username and (message.split(': ')[0] == self.username or
                                              message.split(': ')[0] == 'все'):
                    if 'иди на' in message:
                        data = message.split()

                        if len(data) != 5:
                            self.bot.chat('нет таких координат')
                        else:
                            self.bot.pathfinder.setMovements(movements)
                            self.bot.pathfinder.setGoal(
                                pathfinder.goals.GoalNear(int(data[2]), int(data[3]), int(data[4]), RANGE_GOAL))

                    elif 'иди за мной' in message:
                        player = self.bot.players[user]
                        target = player.entity

                        self.bot.pathfinder.setMovements(movements)
                        goal = GoalFollow(target, 1)
                        self.bot.pathfinder.setGoal(goal, True)

                    elif 'остановись' in message:
                        pos = self.bot.entity.position
                        self.bot.pathfinder.setMovements(movements)
                        self.bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, RANGE_GOAL))

                    elif 'иди ко мне' in message:
                        player = self.bot.players[user]
                        target = player.entity

                        self.bot.pathfinder.setMovements(movements)
                        goal = GoalFollow(target, 1)
                        self.bot.pathfinder.setGoal(goal, False)

                    elif 'ищи алмазы' in message:
                        block = self.bot.findBlock({
                            'matching': mc_data.blocksByName.diamond_ore.id,
                            'maxDistance': 256
                        })

                        if not block:
                            self.bot.chat('бро, ниче рядом нет')
                        else:
                            self.bot.pathfinder.setMovements(movements)
                            goal = GoalBlock(block.position.x, block.position.y + 1, block.position.z)
                            self.bot.chat(f'алмаз на {str(block.position.x)} {str(block.position.y + 1)} {str(block.position.z)}')
                            self.bot.pathfinder.setGoal(goal)

                    elif 'ищи портал' in message:
                        block = self.bot.findBlock({
                            'matching': mc_data.blocksByName.end_portal_frame.id,
                            'maxDistance': 2000
                        })

                        if not block:
                            self.bot.chat('бро, ниче рядом нет')
                        else:
                            self.bot.pathfinder.setMovements(movements)
                            goal = GoalBlock(block.position.x, block.position.y + 1, block.position.z)
                            self.bot.chat(f'портал на {str(block.position.x)} {str(block.position.y + 1)} {str(block.position.z)}')
                            self.bot.pathfinder.setGoal(goal)

                    elif 'рыбачь' == message:
                        if self.bot.inventory.count(self.bot.registry.itemsByName.fishing_rod.id) <= 0:
                            self.bot.chat('У меня в интвентаре нет удочки.')
                        else:
                            def fishing():
                                if self.bot.inventory.count(self.bot.registry.itemsByName.fishing_rod.id) <= 0:
                                    return
                                elif not (
                                        self.bot.heldItem and self.bot.heldItem.type == self.bot.registry.itemsByName.
                                        fishing_rod.id):
                                    rod = self.bot.inventory.findInventoryItem(self.bot.registry.itemsByName.fishing_rod
                                                                               .id)
                                    self.bot.equip(rod, 'hand')
                                    self.bot.chat(
                                        f'Осталось '
                                        f'{self.bot.inventory.count(self.bot.registry.itemsByName.fishing_rod.id)}'
                                        f' удочек.')
                                else:
                                    self.bot.activateItem()
                                sleep(FISHING_INTERVAL)
                                fishing()

                            fishing()
                    elif 'выключайся' in message:
                        self.bot.quit()
                        os._exit(0)

                    elif 'скажи координаты' in message:
                        answer = str(self.bot).split('Vec3')[-4].split('\n')[0][3:-3]
                        self.bot.chat(f"{answer}")
                    else:
                        self.bot.chat('Неизвестная мне команда.')

    def stop(self):
        if self.running:
            self.bot.quit()
        os._exit(0)


if __name__ == '__main__':
    bot = MineBot('bot1', '26.157.37.235:57608', '1.19.4')
    bot.run()
