import json

from calc_damage import Pokemon, Move, Item, Weather, Field, Barrier, CalcDamage

class GuessStatus:
    def __init__(self, file_path:str):
        with open(file_path, 'r', encoding = 'utf-8') as f:
            self.data = json.load(f)

    def get_data_or_default(self, data, key, default):
        if data[key]:
            return data[key]
        else:
            return default

    def make_my_pokemon_from_json(self, data:json) -> Pokemon:
        data = data['my_pokemon']
        ivs = data['iv']
        evs = data['ev']
        ranks = data['rank']
        
        my_poke = Pokemon(
            name = data['name'],
            level = self.get_data_or_default(data, 'level', 50),
            iv_h = self.get_data_or_default(ivs, 'h', 31),
            iv_a = self.get_data_or_default(ivs, 'a', 31),
            iv_b = self.get_data_or_default(ivs, 'b', 31),
            iv_c = self.get_data_or_default(ivs, 'c', 31),
            iv_d = self.get_data_or_default(ivs, 'd', 31),
            iv_s = self.get_data_or_default(ivs, 's', 31),
            ev_h = self.get_data_or_default(evs, 'h', 0),
            ev_a = self.get_data_or_default(evs, 'a', 0),
            ev_b = self.get_data_or_default(evs, 'b', 0),
            ev_c = self.get_data_or_default(evs, 'c', 0),
            ev_d = self.get_data_or_default(evs, 'd', 0),
            ev_s = self.get_data_or_default(evs, 's', 0),
            rank_a = self.get_data_or_default(ranks, 'a', 0),
            rank_b = self.get_data_or_default(ranks, 'b', 0),
            rank_c = self.get_data_or_default(ranks, 'c', 0),
            rank_d = self.get_data_or_default(ranks, 'd', 0),
            rank_s = self.get_data_or_default(ranks, 's', 0),
            nature = self.get_data_or_default(data, 'nature', 'まじめ'),
            ailment = self.get_data_or_default(data, 'ailment', ''),
            is_dynamax = self.get_data_or_default(data, 'is_dynamax', False),
            is_ability_effective = self.get_data_or_default(data, 'is_ability_effective', False)
        )
        my_poke.ability = self.get_data_or_default(data, 'ability', my_poke.ability)
        return my_poke

    def make_ene_pokemon_from_json(self, data:json) -> Pokemon:
        data = data['ene_pokemon']
        ranks = data['rank']
        ene_poke = Pokemon(
            name = data['name'],
            level = self.get_data_or_default(data, 'level', 50),
            rank_a = self.get_data_or_default(ranks, 'a', 0),
            rank_b = self.get_data_or_default(ranks, 'b', 0),
            rank_c = self.get_data_or_default(ranks, 'c', 0),
            rank_d = self.get_data_or_default(ranks, 'd', 0),
            rank_s = self.get_data_or_default(ranks, 's', 0),
            ailment = self.get_data_or_default(data, 'ailment', ''),
            is_dynamax = self.get_data_or_default(data, 'is_dynamax', False),
        )
        return ene_poke

    def make_my_item_from_json(self, data:json) -> Item:
        my_item = Item(data['my_item']['name'])
        return my_item
    def make_my_move_from_json(self, data:json) -> Move:
        my_move = Move(data['move']['name'], data['move']['is_effective'])
        return my_move
    def make_weather_from_json(self, data:json) -> Weather:
        weather = Weather(data['weather'])
        return weather
    def make_field_from_json(self, data:json) -> Field:
        field = Field(data['field'])
        return field
    def make_barrier_from_json(self, data:json) -> Barrier:
        barrier = Barrier(data['barrier'])
        return barrier

    def set_data(self):
        self.my_poke = self.make_my_pokemon_from_json(self.data)
        self.ene_poke = self.make_ene_pokemon_from_json(self.data)
        self.my_item = self.make_my_item_from_json(self.data)
        self.my_move = self.make_my_move_from_json(self.data)
        self.weather = self.make_weather_from_json(self.data)
        self.field = self.make_field_from_json(self.data)
        self.barrier = self.make_barrier_from_json(self.data)

    def check_damage(self, damage):
        self.ene_poke.calc_max_status()
        self.ene_poke.calc_min_status()
        status_in_calc = []
        for status in range(self.ene_poke.min_d, self.ene_poke.max_d+1):
            self.ene_poke.status_d = status
            calc = CalcDamage(
                move=self.my_move, 
                atk_poke=self.my_poke, 
                def_poke=self.ene_poke, 
                atk_item=self.my_item, 
                weather=self.weather, 
                field=self.field, 
                barrier=self.barrier
            )
            damages = calc.calc_damage()
            damage_max = damages[15]
            damage_min = damages[0]
            if damage > damage_max:
                break
            if damage >= damage_min:
                status_in_calc.append(status)
        
        if len(status_in_calc) == 0:
            print('そのようなダメージはあり得ません。')
            return 0,0

        return status_in_calc[0], status_in_calc[-1]

    def calc_range_ev_iv(self, min, max, nature):
        self.ene_poke.nature = nature
        self.ene_poke.ev_b = 0
        self.ene_poke.ev_d = 0
        min_flag = False
        max_flag = False
        condition = {}
        category = self.my_move.category

        for iv in range(0,32):
            self.ene_poke.iv_b = iv
            self.ene_poke.iv_d = iv
            self.ene_poke.calc_status()
            if self.ene_poke.status_d > max:
                condition['min'] = {'iv':'null', 'ev':'null'}
                break
            if self.ene_poke.status_d >= min:
                condition['min'] = {'iv':iv, 'ev':0}
                min_flag = True
                break
        for ev in range(0,253):
            if min_flag:
                break
            self.ene_poke.ev_d = ev
            self.ene_poke.calc_status()
            if self.ene_poke.status_d >= min:
                condition['min'] = {'iv':iv, 'ev':ev}
                min_flag = True
                break
        self.ene_poke.iv_d = 31
        for ev in range(252,-1, -1):
            self.ene_poke.ev_d = ev
            self.ene_poke.calc_status()
            if self.ene_poke.status_d < min:
                max_flag=True
                condition['max'] = {'iv':'null', 'ev':'null'}
                break
            if self.ene_poke.status_d <= max:
                condition['max'] = {'iv':31, 'ev':ev}
                max_flag=True
                break
        for iv in range(31,-1, -1):
            if max_flag:
                break
            self.ene_poke.iv_d = iv
            self.ene_poke.calc_status()
            if self.ene_poke.status_d <= max:
                condition['max'] = {'iv':iv, 'ev':0}
                min_flag = True
                break

        return condition