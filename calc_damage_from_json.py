from libs.calc_damage import Move, Pokemon, Item, Weather, Field, Barrier, CalcDamage
import json


class CalcDamageFromJson:
    def __init__(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def get_data_or_default(self, data, key, default):
        if data[key]:
            return data[key]
        else:
            return default

    def make_pokemon(self, side, data: json) -> Pokemon:
        data = data[side]
        ivs = data["iv"]
        evs = data["ev"]
        ranks = data["rank"]
        poke = Pokemon(
            name=self.get_data_or_default(data, "name", ""),
            level=self.get_data_or_default(data, "level", 50),
            iv_h=self.get_data_or_default(ivs, "h", 31),
            iv_a=self.get_data_or_default(ivs, "a", 31),
            iv_b=self.get_data_or_default(ivs, "b", 31),
            iv_c=self.get_data_or_default(ivs, "c", 31),
            iv_d=self.get_data_or_default(ivs, "d", 31),
            iv_s=self.get_data_or_default(ivs, "s", 31),
            ev_h=self.get_data_or_default(evs, "h", 0),
            ev_a=self.get_data_or_default(evs, "a", 0),
            ev_b=self.get_data_or_default(evs, "b", 0),
            ev_c=self.get_data_or_default(evs, "c", 0),
            ev_d=self.get_data_or_default(evs, "d", 0),
            ev_s=self.get_data_or_default(evs, "s", 0),
            rank_a=self.get_data_or_default(ranks, "a", 0),
            rank_b=self.get_data_or_default(ranks, "b", 0),
            rank_c=self.get_data_or_default(ranks, "c", 0),
            rank_d=self.get_data_or_default(ranks, "d", 0),
            rank_s=self.get_data_or_default(ranks, "s", 0),
            nature=self.get_data_or_default(data, "nature", "まじめ"),
            ailment=self.get_data_or_default(data, "ailment", ""),
            is_dynamax=self.get_data_or_default(data, "is_dynamax", False),
            is_ability_effective=self.get_data_or_default(
                data, "is_ability_effective", False
            ),
        )
        poke.ability = self.get_data_or_default(data, "ability", poke.ability)
        return poke

    def make_item(self, side, data: json) -> Item:
        item = Item(data[side]["name"])
        return item

    def make_move(self, data: json) -> Move:
        move = Move(data["move"]["name"], data["move"]["is_effective"])
        return move

    def make_weather(self, data: json) -> Weather:
        weather = Weather(data["weather"]["name"])
        return weather

    def make_field(self, data: json) -> Field:
        field = Field(data["field"]["name"])
        return field

    def make_barrier(self, data: json) -> Barrier:
        barrier = Barrier(data["barrier"]["name"])
        return barrier

    def make_is_critical(self, data: json) -> bool:
        return self.get_data_or_default(data, "is_critical", False)

    def calc_damage(self):
        move = self.make_move(self.data)
        atk_poke = self.make_pokemon("atk_poke", self.data)
        def_poke = self.make_pokemon("def_poke", self.data)
        atk_friend_poke = self.make_pokemon("atk_friend_poke", self.data)
        def_friend_poke = self.make_pokemon("def_friend_poke", self.data)
        atk_item = self.make_item("atk_item", self.data)
        def_item = self.make_item("def_item", self.data)
        weather = self.make_weather(self.data)
        field = self.make_field(self.data)
        barrier = self.make_barrier(self.data)
        is_critical = self.make_is_critical(self.data)
        calc = CalcDamage(
            move,
            atk_poke,
            def_poke,
            atk_friend_poke,
            def_friend_poke,
            atk_item,
            def_item,
            field,
            weather,
            barrier,
            is_critical,
        )
        return calc.calc_damage()
