from game import Snake, Game

from numpy import dot, array, where
from numpy.random import uniform as np_uniform
from random import randint, uniform


class NNSnake:
    def __init__(self, x=5, y=5, start_long=5, direction=2, weights=None, chance_of_mutation=0.1, min_long = 4):
        self.x = x
        self.y = y
        self.long = start_long
        self.min_long = min_long
        self.direction = direction
        self._create_segments(start_long)

        self.lifetime = 0

        self.chance_of_mutation = chance_of_mutation

        self._create_weights(weights)

    def _create_segments(self, long):
        self.segments = []
        for i in range(long):
            self.segments.append([self.x, self.y])

    def _create_weights(self, weights):
        if type(weights) == type(None):
            self.weights = np_uniform(-0.5, 0.5, (3, 9))
        elif len(weights) == 3 and len(weights[0]) == 9:
            self.weights = weights
        else:
            raise ValueError('Длинна переданно массива весовне совместива с обзором, '
                             'требуется (3, 9) длинна масива весов')

    def _calculation(self, inp):
        out = self.weights.dot(inp)
        return where(out == max(out))[0][0]


    def move(self):
        for i in range(self.long - 1, 0, -1):
            previous_segment = self.segments[i - 1]
            self.segments[i][0] = previous_segment[0]
            self.segments[i][1] = previous_segment[1]

        previous_segment = self.segments[0]
        if self.direction % 2 == 0:
            self.segments[0][0] = previous_segment[0]
            self.segments[0][1] = previous_segment[1] + (-3 + self.direction)
        else:
            self.segments[0][0] = previous_segment[0] + (-2 + self.direction)
            self.segments[0][1] = previous_segment[1]

        self.x = previous_segment[0]
        self.y = previous_segment[1]

    def add_segment(self):
        """ Добавляет сегмент в конец змейки. Сегмент становится виден после вызова move. """
        previous_segment = self.segments[-1]
        self.segments.append([previous_segment[0], previous_segment[1]])
        self.long += 1

    def pop_segment(self):
        """ Удаляет последний сегмент. """
        self.segments.pop()

    def get_position(self):
        return tuple(((segment[0], segment[1]) for segment in self.segments))

    def mutation(self):
        c_weights = self.weights.copy()
        for i in range(len(c_weights)):
            for k in range(len(c_weights[i])):
                if uniform(0, 1) < self.chance_of_mutation:
                    c_weights[i, k] += uniform(-0.1, 0.1)
        return c_weights

    def division(self):
        new_weights = self.mutation()
        if self.long > self.min_long * 2:
            long = self.long // 2

            new_snake = NNSnake(x=self.segments[-long][0], y=self.segments[-long][1], start_long=long,
                                direction=self.direction, weights=new_weights)
            for i in range(long):
                self.pop_segment()
            self.long -= long
            return new_snake
        else:
            return False

    def _get_visibility(self, field, block, empty, segment, food):
        lx = len(field[0])
        ly = len(field)

        visibility = []

        if self.direction % 2 == 0:
            dy = (-3 + self.direction)
            dx = 0
        else:
            dx = (-2 + self.direction)
            dy = 0
        for i in range(3):
            if dy:  # Поиск ближайшей еды и припятсвий по оси y если нас интересует ось y.
                visibility.append(1 / (ly - self.y if dy > 0 else self.y))
                for y in range(self.y + dy, (ly if dy > 0 else -1), dy):
                    if (field[y][self.x] == food) and \
                            (len(visibility) < (i + 1) * 3 - 1):
                        visibility.append(1 / ((y - self.y) * dy))
                    elif (field[y][self.x] != empty) and \
                            (len(visibility) == (i + 1) * 3 - 1):
                        visibility.append(1 / ((y - self.y) * dy))
                        break
                    elif (field[y][self.x] != empty):
                        visibility.append(0)
                        visibility.append(1 / ((y - self.y) * dy))
                        break

            if dx:  # Поиск ближайшей еды и припятсвий по оси x если нас интересует ось x.
                visibility.append(1 / (lx - self.x if dy > 0 else self.x))
                for x in range(self.x + dx, (lx if dx > 0 else -1), dx):
                    if (field[self.y][x] == food) and (len(visibility) < (i + 1) * 3 - 1):
                        visibility.append(1 / ((x - self.x) * dx))
                    elif (field[self.y][x] != empty) and \
                            (len(visibility) == (i + 1) * 3 - 1):
                        visibility.append(1 / ((x - self.x) * dx))
                        break
                    elif field[self.y][x] != empty:
                        visibility.append(0)
                        visibility.append(1 / ((x - self.x) * dx))
                        break
            if i < 2:
                for k in range(i + 1):  # Смена активной оси.
                    if dx:
                        dx, dy = dx - dx, dy - dx
                    elif dy:
                        dx, dy = dx + dy, dy - dy
        return visibility

    def update(self, field, block='X', empty=' ', segment='O', food='#'):
        visibility_axis = self._get_visibility(field, block, empty, segment, food)
        d_dir = self._calculation(visibility_axis) - 1
        self.direction += d_dir
        if self.direction < 1:
            self.direction += 4
        if self.direction > 4:
            self.direction -= 4


class GameMod:
    def __init__(self, size, nums_foods, nums_snakes, nums_blocks, moves_after_division, block='X', empty=' ', segment='O', food='#'):
        self.size = size
        self.block = block
        self.segment = segment
        self.food = food
        self.empty = empty
        self._moves_after_division = moves_after_division

        self.iteration = 0
        self.eaten = 0
        self.moves_after_division = 0

        self.foods = []
        self.blocks = []
        self.snakes = []

        self.playing_field = self._create_playing_field()

        self._create_block(nums_blocks)
        self._create_snakes(nums=nums_snakes)
        self._create_food(nums_foods)

    def _create_block(self, nums):
        pass

    def _create_snakes(self, nums):
        field = ''.join([''.join(s) for s in self.get_playing_field()])
        for i in range(nums):
            if ' ' in field:
                while True:
                    x = randint(field.find(' '), len(field) - field[::-1].find(' '))
                    if field[x] == ' ':
                        self.snakes.append(NNSnake(x % (self.size[0]), x // (self.size[0]), min_long=3))
                        break
            else:
                break

    def _create_snakes_w(self, weights):
        field = ''.join([''.join(s) for s in self.get_playing_field()])
        if ' ' in field:
            while True:
                x = randint(field.find(' '), len(field) - field[::-1].find(' '))
                if field[x] == ' ':
                    self.snakes.append(NNSnake(x % (self.size[0]), x // (self.size[0]), min_long=3, weights=weights))
                    break

    def _create_food(self, nums):
        field = ''.join([''.join(s) for s in self.get_playing_field()])
        for i in range(nums):
            if ' ' in field:
                while True:
                    x = randint(field.find(' '), len(field) - field[::-1].find(' ') - 1)
                    if field[x] == ' ':
                        self.foods.append((x % (self.size[0]), x // (self.size[0])))
                        break
            else:
                break

    def _create_playing_field(self):
        field = [[self.block for i in range(self.size[0])]]
        for y in range(self.size[1] - 2):
            field.append([self.block] + [self.empty for i in range(self.size[0] - 2)] + [self.block])
        field.append([self.block for i in range(self.size[0])])
        return field

    def _get_copy_playing_field(self):
        playing_field = [line.copy() for line in self.playing_field]
        return playing_field

    def _placement_of_objects(self):
        playing_field = self._get_copy_playing_field()
        for block in self.blocks:
            playing_field[block[1]][block[0]] = self.block

        for food in self.foods:
            try:
                playing_field[food[1]][food[0]] = self.food
            except:
                print('ошибка еды', food)

        for snake in self.snakes:
            for segment in snake.segments[1:]:
                playing_field[segment[1]][segment[0]] = self.segment
        return playing_field

    def _game_move(self):
        playing_field = self._placement_of_objects()
        for snake in self.snakes:
            snake.move()

            if playing_field[snake.y][snake.x] == self.block:
                self.snakes.remove(snake)
                break
            if playing_field[snake.y][snake.x] == self.segment:
                self.snakes.remove(snake)
                break

            if playing_field[snake.y][snake.x] == self.food:
                playing_field[snake.y][snake.x] = self.segment
                snake.add_segment()
                self.foods.remove((snake.x, snake.y))
                self._create_food(1)
            if playing_field[snake.y][snake.x] == self.empty:
                playing_field[snake.y][snake.x] = self.segment

            snake.update(playing_field)

    def update(self):
        self._game_move()
        self.iteration += 1
        self.moves_after_division += 1
        if self.iteration % self._moves_after_division == 0 and self.iteration < 4000:
            l_del = []
            for food in self.foods[: len(self.foods) // 10]:
                self.foods.remove(food)
            for i in range(len(self.snakes)):
                snake = self.snakes[i]
                snake.lifetime += 1
                new_snake = snake.division()
                if new_snake:
                    self.moves_after_division = 0
                    self._create_snakes_w(weights=snake.weights)
                    if i < len(self.snakes) - 1:
                        new_weights1 = []
                        new_weights2 = []
                        weights = [new_snake.weights, self.snakes[i + 1].weights]

                        for i in range(len(weights[0])):
                            new_weights1.append([])
                            new_weights2.append([])
                            for k in range(len(weights[0][i])):
                                new_weights1[i].append(weights[randint(0, 1)][i][k])
                                new_weights2[i].append(weights[randint(0, 1)][i][k])
                        new_weights1 = array(new_weights1)
                        new_weights2 = array(new_weights2)
                        self._create_snakes_w(weights=new_weights1)
                        self._create_snakes_w(weights=new_weights2)
                else:
                    l_del.append(snake)
            for snake in l_del:
                self.snakes.remove(snake)
            l_del = []

    def get_playing_field(self):
        playing_field = self._placement_of_objects()
        for snake in self.snakes:
            segment = snake.segments[0]
            playing_field[segment[1]][segment[0]] = self.segment
        return playing_field


if __name__ == '__main__':
    time_learn = 4000
    from time import sleep
    from os import system

    while True:
        game = GameMod((260, 70), 1000, 2000, 0, 100)
        while game.snakes:
            game.update()
            if game.iteration == time_learn:
                input()
            if game.iteration > time_learn:
                sleep(0.1)
            system('clear')

            if game.iteration > time_learn:
                print('\n'.join([''.join(s) for s in game.get_playing_field()]))

            print('Ходов после последнего деления', game.moves_after_division)
            print('Номер итерации', game.iteration)
            print('Змеек на сцене', len(game.snakes))
