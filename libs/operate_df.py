import pandas as pd
import numpy as np
from tqdm.auto import tqdm
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from libs.calc_damage import Pokemon, Move, Item, CalcDamage


def make_df(
    cell_data: list, is_nan_check: bool = False, checked_column: bool = "pokemon"
):
    df = pd.DataFrame(cell_data[1:], columns=cell_data[0])
    # 空白行を削除するため
    if is_nan_check:
        df[checked_column].replace("", np.nan, inplace=True)
        df.dropna(subset=[checked_column], inplace=True)
    return df


def set_my_data(pokemon_dict):
    """自分のポケモン情報をPokemon,Move,Itemクラスに格納する"""
    pokemon = Pokemon(
        name=pokemon_dict["pokemon"],
        ev_h=pokemon_dict["ev_HP"],
        ev_a=pokemon_dict["ev_A"],
        ev_b=pokemon_dict["ev_B"],
        ev_c=pokemon_dict["ev_C"],
        ev_d=pokemon_dict["ev_D"],
        ev_s=pokemon_dict["ev_S"],
        iv_h=pokemon_dict["iv_HP"],
        iv_a=pokemon_dict["iv_A"],
        iv_b=pokemon_dict["iv_B"],
        iv_c=pokemon_dict["iv_C"],
        iv_d=pokemon_dict["iv_D"],
        iv_s=pokemon_dict["iv_S"],
        nature=pokemon_dict["nature"],
        ability=pokemon_dict["Ability"],
    )
    move_1 = Move(name=pokemon_dict["move_1"])
    move_2 = Move(name=pokemon_dict["move_2"])
    move_3 = Move(name=pokemon_dict["move_3"])
    move_4 = Move(name=pokemon_dict["move_4"])
    item = Item(pokemon_dict["Item"])
    return pokemon, move_1, move_2, move_3, move_4, item


def set_enemy_data(pokemon_dict):
    pokemon_0 = Pokemon(name=pokemon_dict["pokemon"], ability=pokemon_dict["Ability"])
    pokemon_252 = Pokemon(
        name=pokemon_dict["pokemon"],
        ability=pokemon_dict["Ability"],
        ev_h=252,
        ev_a=252,
        ev_b=252,
        ev_c=252,
        ev_d=252,
        ev_s=252,
    )
    pokemon_252up = Pokemon(
        name=pokemon_dict["pokemon"],
        ability=pokemon_dict["Ability"],
        ev_h=252,
        ev_a=252,
        ev_b=252,
        ev_c=252,
        ev_d=252,
        ev_s=252,
        nature="上昇",
    )
    move = Move(pokemon_dict["move"])
    return pokemon_0, pokemon_252, pokemon_252up, move


def set_def_data(pokemon_dict):
    pokemon_0 = Pokemon(name=pokemon_dict["pokemon"], ability=pokemon_dict["Ability"])
    pokemon_h252bd0 = Pokemon(
        name=pokemon_dict["pokemon"],
        ability=pokemon_dict["Ability"],
        ev_h=252,
        ev_a=252,
        ev_b=0,
        ev_c=252,
        ev_d=0,
        ev_s=252,
    )
    pokemon_h0bd252 = Pokemon(
        name=pokemon_dict["pokemon"],
        ability=pokemon_dict["Ability"],
        ev_h=0,
        ev_a=252,
        ev_b=252,
        ev_c=252,
        ev_d=252,
        ev_s=252,
    )
    pokemon_252 = Pokemon(
        name=pokemon_dict["pokemon"],
        ability=pokemon_dict["Ability"],
        ev_h=252,
        ev_a=252,
        ev_b=252,
        ev_c=252,
        ev_d=252,
        ev_s=252,
    )
    pokemon_252up = Pokemon(
        name=pokemon_dict["pokemon"],
        ability=pokemon_dict["Ability"],
        ev_h=252,
        ev_a=252,
        ev_b=252,
        ev_c=252,
        ev_d=252,
        ev_s=252,
        nature="上昇",
    )
    move = Move(pokemon_dict["move"])
    return pokemon_0, pokemon_h252bd0, pokemon_h0bd252, pokemon_252, pokemon_252up, move


def calc_min_max_damage_raito(calc_data: CalcDamage):
    """最小と最大ダメージ割合をList出力する。"""
    damages = calc_data.calc_damage()
    return [
        round(damages[0] / calc_data.def_poke.status_h * 100, 1),
        round(damages[15] / calc_data.def_poke.status_h * 100, 1),
    ]


def calc_min_max_damage(calc_data: CalcDamage):
    """最小と最大ダメージをList出力する。"""
    damages = calc_data.calc_damage()
    return [damages[0], damages[15]]


def extract_my_attack_info(calc_data: CalcDamage):
    """自分ポケモン用情報を出力する。

    return [自分攻撃ポケモン名, ]
    """
    return [calc_data.atk_poke_name, calc_data.def_poke_name, calc_data.def_ability]


def make_atk_calc_data(my_pokemon_list, ene_pokemon_list):
    output_data = []
    for my_poke_dict in tqdm(my_pokemon_list, desc="自分ポケモンからのダメージ計算"):
        my_pokemon, move_1, move_2, move_3, move_4, my_item = set_my_data(my_poke_dict)
        output_data_my_pokemon = [my_pokemon.name]
        for ene_poke_dict in tqdm(ene_pokemon_list, mininterval=0.5):
            (
                enemy_pokemon_0,
                enemy_pokemon_252,
                enemy_pokemon_252_up,
                enemy_move,
            ) = set_enemy_data(ene_poke_dict)
            output_data_my_pokemon.extend(
                [enemy_pokemon_0.name, enemy_pokemon_0.ability]
            )
            for move in [move_1, move_2, move_3, move_4]:
                output_data_my_pokemon.extend([move.name])
                for ene_pokemon in [
                    enemy_pokemon_0,
                    enemy_pokemon_252,
                    enemy_pokemon_252_up,
                ]:
                    calc = CalcDamage(move, my_pokemon, ene_pokemon, atk_item=my_item)
                    output_data_my_pokemon.extend(calc_min_max_damage_raito(calc))
                output_data.append(output_data_my_pokemon)
                output_data_my_pokemon = output_data_my_pokemon[:3]
            output_data_my_pokemon = output_data_my_pokemon[:1]
    return output_data


def make_def_calc_data(my_pokemon_list, ene_pokemon_list):
    """相手ポケモンからの被ダメを計算する。"""
    output_def_data = []
    for my_poke_dict in tqdm(my_pokemon_list, desc="相手ポケモンからのダメージ計算"):
        my_pokemon, move_1, move_2, move_3, move_4, my_item = set_my_data(my_poke_dict)
        output_data_my_pokemon = [my_pokemon.name]
        for ene_poke_dict in tqdm(ene_pokemon_list, mininterval=0.5):
            (
                enemy_pokemon_0,
                enemy_pokemon_252,
                enemy_pokemon_252_up,
                enemy_move,
            ) = set_enemy_data(ene_poke_dict)
            output_data_my_pokemon.extend(
                [enemy_pokemon_0.name, enemy_pokemon_0.ability, enemy_move.name]
            )
            for enemy_pokemon in [
                enemy_pokemon_0,
                enemy_pokemon_252,
                enemy_pokemon_252_up,
            ]:
                calc = CalcDamage(
                    enemy_move, enemy_pokemon, my_pokemon, def_item=my_item
                )
                output_data_my_pokemon.extend(calc_min_max_damage(calc))
            output_def_data.append(output_data_my_pokemon)
            output_data_my_pokemon = output_data_my_pokemon[:1]
    return output_def_data


def extract_pokemon_ability_df(df_enemy: pd.DataFrame):
    """相手ポケモン、アイテムごとにデータ取得"""
    output_list = []
    for i in df_enemy["pokemon"].unique():
        item_a = df_enemy[df_enemy["pokemon"] == i]["Ability"].unique()
        for j in item_a:
            output_list.append(
                df_enemy.to_dict(orient="records")[
                    df_enemy.query("pokemon == '{}' and Ability == '{}'".format(i, j))
                    .head(1)
                    .index[0]
                ]
            )
    return output_list


def make_calc_data(pokemon_list, pokemon_def_list):
    """ポケモン情報から攻め受け全対応のダメ計計算結果を出力する"""
    output_data = []
    for atk_poke_dict in tqdm(pokemon_list, desc="相手ポケモンからのダメージ計算"):
        atk_pokemon_0, atk_pokemon_252, atk_pokemon_252up, move = set_enemy_data(
            atk_poke_dict
        )
        output_one_data = [atk_pokemon_0.name, atk_pokemon_0.ability, move.name]
        for def_poke_dict in pokemon_def_list:
            (
                def_pokemon_0,
                def_pokemon_h252bd0,
                def_pokemon_h0bd252,
                def_pokemon_252,
                def_pokemon_252up,
                move_a,
            ) = set_def_data(def_poke_dict)
            output_one_data.extend([def_pokemon_0.name, def_pokemon_0.ability])
            for atk_pokemon in [atk_pokemon_0, atk_pokemon_252, atk_pokemon_252up]:
                for def_pokemon in [
                    def_pokemon_0,
                    def_pokemon_h252bd0,
                    def_pokemon_h0bd252,
                    def_pokemon_252,
                    def_pokemon_252up,
                ]:
                    calc = CalcDamage(move, atk_pokemon, def_pokemon)
                    output_one_data.extend(calc_min_max_damage_raito(calc))
            output_data.append(output_one_data)
            output_one_data = output_one_data[0:3]
    return output_data
