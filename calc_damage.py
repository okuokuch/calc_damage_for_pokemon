import pandas as pd
import math
import os

pwd = os.getcwd()

#csvは完成してません。
df_poke = pd.read_csv(pwd+'\\asset\\poke.csv')
df_move = pd.read_csv(pwd+'\\asset\\move.csv')#追加効果はやけどまで。
df_nature = pd.read_csv(pwd+'\\asset\\nature.csv')
df_type = pd.read_csv(pwd+'\\asset\\type.csv')
df_last_power_factor = pd.read_csv(pwd+'\\asset\\last_power_factor.csv')
df_last_atk_factor = pd.read_csv(pwd+'\\asset\\last_atk_factor.csv')
df_last_def_factor = pd.read_csv(pwd+'\\asset\\last_def_factor.csv')
df_damage_factor = pd.read_csv(pwd+'\\asset\\damage_factor.csv')
df_weather_factor = pd.read_csv(pwd+'\\asset\\weather_factor.csv')
df_item = pd.read_csv(pwd+'\\asset\\item.csv')
df_field = pd.read_csv(pwd+'\\asset\\field.csv')
df_weather = pd.read_csv(pwd+'\\asset\\weather.csv')
df_barrier = pd.read_csv(pwd+'\\asset\\barrier.csv')

class ConvertToInt:
    """数値を整数(Int型)に変換する
    
    round5_5は五捨五超入
    rond4_5は四捨五入
    floorは切り捨て
    を行う。
    """
    def round5_5(self, number):
        return math.ceil(number-0.5)

    def round4_5(self, number):
        return math.floor(number+0.5)

    def floor(self, number):
        return  math.floor(number)

class CalcCorrectionValue(ConvertToInt):
    """補正値を計算する
    
    汎用的な計算3種類をメソッド化
    """

    def multiply_factor_round4_5(self, origin:int, factor:int):
        value = self.round4_5(origin*factor/4096)
        return value

    def multiply_factor_round5_5(self, origin:int, factor:int):
        value = self.round5_5(origin*factor/4096)
        return value

    def multiply_factor_floor(self, origin:int, factor:int):
        value = self.floor(origin*factor/4096)
        return value

class OperateDataFrme:
    """Pandasのdfでよく使用する操作をまとめたクラス"""
    def extract_info(self, df, column):
        """dfから情報を抽出する。"""
        info = df[column].values[0]
        return info
    
    def has_record(self, df, column, search):
        """dfにデータがあるか確認する"""
        try:
            num_records = len(df[df[column]==search])
        except KeyError as e:
            print('カラム名が間違っています。')
            print(e.args)
        if num_records == 0:
            return False
        else:
            return True
    
    def convert_boolean_to_str_list(self, boolean):
        """boolean型を['TRUE' or 'FALSE', 'any']に変換する。
        
        !!csvの空欄をanyで埋めている→bool型のカラムがbool型と判定されない。
        →文字列として処理する仕様。
        もっと良い仕様がありそう。。。
        """
        if boolean:
            return ['TRUE', 'any']
        else:
            return ['FALSE', 'any']
    
    def make_searching_condition(self, arg):
        """dfの検索用の条件を作成する。
        
        変数が存在する場合はリスト型、変数が存在しない場合は'any'を返す。
        !!csvの書式の都合で、[検索したい値 or any]というリストを作成している。
        もっと良い仕様がありそう。
        """
        if type(arg) == bool:
            self.convert_boolean_to_str_list(arg)
        
        #bool型でなければ以下処理に移る。
        try:
            return [arg, 'any']
        except AttributeError:
            return ['', 'any']
    
    def make_matched_df(self, df:pd, **keyargs):
        """マスタdfから条件に合致するレコードのdfを作成する"""
        matched_df = df.copy()
        for key, value in keyargs.items():
            value = self.make_searching_condition(value)
            matched_df = matched_df[(matched_df[key] == value[0]) | (matched_df[key] == value[1])]
        return matched_df

class Rank:
    """ランク補正を補正値に変換"""
    def make_rank_magnification(self, num):
        num = int(num)
        if num >= 6:
            #6以上であれば、6として処理
            magnification = (6+2)/2
        elif num >= 0:
            magnification = (num+2)/2
        elif num >= -6:
            magnification = 2/(2-num)
        else:
            #-6以下であれば、-6として処理
            magnification = 2/(2+6)
        return magnification

class Pokemon(ConvertToInt, OperateDataFrme, Rank):
    """ポケモンの情報をまとめたクラス。
    
    """
    def __init__(
        self, 
        name,
        level = 50,
        ev_h = 0,
        ev_a = 0,
        ev_b = 0,
        ev_c = 0,
        ev_d = 0,
        ev_s = 0,
        iv_h = 31,
        iv_a = 31,
        iv_b = 31,
        iv_c = 31,
        iv_d = 31,
        iv_s = 31,
        rank_a = 0,
        rank_b = 0,
        rank_c = 0,
        rank_d = 0,
        rank_s = 0,
        nature = 'まじめ',
        ailment = '',
        is_dynamax = False,
        is_ability_effective = False
    ):
        self.name = name
        self.level = level
        self.ev_h = ev_h
        self.ev_a = ev_a
        self.ev_b = ev_b
        self.ev_c = ev_c
        self.ev_d = ev_d
        self.ev_s = ev_s
        self.iv_h = iv_h
        self.iv_a = iv_a
        self.iv_b = iv_b
        self.iv_c = iv_c
        self.iv_d = iv_d
        self.iv_s = iv_s
        self.rank_a = rank_a
        self.rank_b = rank_b
        self.rank_c = rank_c
        self.rank_d = rank_d
        self.rank_s = rank_s
        self.nature = nature
        self.ailment = ailment
        self.is_dynamax = is_dynamax
        self.is_ability_effective = is_ability_effective
        if self.name != '':
            self.load_base_info()
            self.calc_status()
            try:
                self.ability = self.ability1
            except AttributeError as e:
                print('特性を設定できませんでした。')
                print(e.args)
                self.ability = ''
        else:
            #!!初期値として''でインスタンス作成する場合のエラー出力回避
            self.ability=''
    
    def load_base_info(self):
        """ポケモン名から、基礎情報とステータスの変更を行う。"""
        self.base_info_df = df_poke[df_poke['name'] == self.name]
        try:
            self.bs_h = self.extract_info(self.base_info_df, 'hp')
            self.bs_a = self.extract_info(self.base_info_df, 'a')
            self.bs_b = self.extract_info(self.base_info_df, 'b')
            self.bs_c = self.extract_info(self.base_info_df, 'c')
            self.bs_d = self.extract_info(self.base_info_df, 'd')
            self.bs_s = self.extract_info(self.base_info_df, 's')
            self.type1 = self.extract_info(self.base_info_df, 'type1')
            self.type2 = self.extract_info(self.base_info_df, 'type2')
            self.ability1 = self.extract_info(self.base_info_df, 'ability1')
            self.ability2 = self.extract_info(self.base_info_df, 'ability2')
            self.ability3 = self.extract_info(self.base_info_df, 'ability3')
            self.weight_move_power = self.extract_info(self.base_info_df, 'weight_move')
            self.is_fully_evolved = self.extract_info(self.base_info_df, 'is_fully_evolved')
        except IndexError as e:
            print('ポケモンの基礎データを取得できませんでした。')
            print(e.args)

    def calc_hp(self, level, bs, iv, ev):
        return self.floor((bs*2+iv+self.floor(ev/4))\
                   *level/100)+level+10

    def calc_abcds(self, level, status, bs, iv, ev, rank, nature):
        nature_factor = df_nature[df_nature["name"]==nature][status].values[0] 
        base_status =  self.floor((self.floor((bs*2+iv+self.floor(ev/4))\
                          *level/100+5))*nature_factor)
        rank_factor = self.make_rank_magnification(rank)
        return self.floor(base_status*rank_factor)
    
    def calc_status(self):
        """レベル、個体値、努力値、性格をもとにステータスを計算する。"""
        try:
            #!!個体値や種族値の範囲が設定値より大きい場合に補正する記述入れる。
            self.status_h = self.calc_hp(self.level, self.bs_h, self.iv_h, self.ev_h)
            self.status_a = self.calc_abcds(self.level, 'a', self.bs_a, self.iv_a, self.ev_a, self.rank_a, self.nature)
            self.status_b = self.calc_abcds(self.level, 'b', self.bs_b, self.iv_b, self.ev_b, self.rank_b,self.nature)
            self.status_c = self.calc_abcds(self.level, 'c', self.bs_c, self.iv_c, self.ev_c, self.rank_c,self.nature)
            self.status_d = self.calc_abcds(self.level, 'd', self.bs_d, self.iv_d, self.ev_d, self.rank_d,self.nature)
            self.status_s = self.calc_abcds(self.level, 's', self.bs_s, self.iv_s, self.ev_s, self.rank_s,self.nature)
        except AttributeError as e:
            print('ステータス計算に用いる値がありません。')
            print(e.args)
    
    def reload_base_info_and_status(self):
        """基礎情報を再取得し、ステータス計算を行う。"""
        self.load_base_info()
        self.calc_status()

class Move(OperateDataFrme):
    """技の情報をまとめたクラス。"""
    def __init__(self, name, is_effective = True):
        self.name = name
        self.move_info_df = df_move[df_move['name'] == self.name]
        if self.name !='':
            #!!if文は、初期値として''を入力する場合のエラー出力回避が目的
            try:
                #!!変化技の場合や、固定威力がない技(アシパやジャイロボール)の場合int型への変換でエラーが出る。
                #!!特殊な技の計算は空いた能力にも依存するケースが多いので、CalcDamgeクラスに条件を記述する。
                self.type = self.extract_info(self.move_info_df, 'type')
                power = self.extract_info(self.move_info_df, 'power')
                try:
                    self.power = int(power)
                except ValueError:
                    self.power = 0
                power_dynamax = self.extract_info(self.move_info_df, 'power_dynamax')
                try:
                    self.power_dynamax = int(power_dynamax)
                except ValueError:
                    self.power_dynamax = 0
                self.category = self.extract_info(self.move_info_df, 'power_dynamax')
                self.target = self.extract_info(self.move_info_df, 'target')
                self.is_additional_effects = self.extract_info(self.move_info_df, 'is_additional_effects')  #追加効果技
                self.is_biting = self.extract_info(self.move_info_df, 'is_biting')                          #かみつき技
                self.is_contact = self.extract_info(self.move_info_df, 'is_contact')                        #直接技
                self.is_pulse = self.extract_info(self.move_info_df, 'is_pulse')                            #波動技
                self.is_punching = self.extract_info(self.move_info_df, 'is_punching')                      #こぶし技
                self.is_recoil = self.extract_info(self.move_info_df, 'is_recoil')                          #反動技
                self.is_sound = self.extract_info(self.move_info_df, 'is_sound')                            #音技
            except IndexError as e:
                self.type=''
                self.power = 0
                self.power_dynamax = 0
                self.category = ''
                print('技が見つかりませんでした')
                print(e.args)

        self.is_effective = is_effective                                                            #効果判定をどうするか

class Item(OperateDataFrme):
    """アイテムの情報をまとめたクラス。
    """
    def __init__(self, name):
        """アイテム名が正しければ、nameを設定。"""
        if self.has_record(df_item, 'name', name):
            self.name = name
        else:
            self.name = ''

class Weather(OperateDataFrme):
    """天候の情報をまとめたクラス。"""
    def __init__(self, name):
        """アイテム名が正しければ、nameを設定。"""
        if self.has_record(df_weather, 'name', name):
            self.name = name
        else:
            self.name = ''

class Field(OperateDataFrme):
    """フィールドの情報をまとめたクラス。"""
    def __init__(self, name):
        """アイテム名が正しければ、nameを設定。"""
        if self.has_record(df_field, 'name', name):
            self.name = name
        else:
            self.name = ''

class Barrier(OperateDataFrme):
    """壁の情報をまとめたクラス。"""
    def __init__(self, name):
        """アイテム名が正しければ、nameを設定。"""
        if self.has_record(df_barrier, 'name', name):
            self.name = name
        else:
            self.name = ''

class TypeCorrection(OperateDataFrme):
    def __init__(self, move:Move, atk_poke:Pokemon, def_poke:Pokemon):
        self.move = move
        self.atk_poke = atk_poke
        self.def_poke = def_poke
        self.set_data_for_type_correction_calc()
        self.set_type_effectiveness()
        self.set_same_type_factor()

    def set_data_for_type_correction_calc(self):
        """タイプ相性計算に必要な変数をインスタンス変数に格納する。"""
        self.move_type = self.move.type
        self.atk_type1 = self.atk_poke.type1
        self.atke_type2 = self.atk_poke.type2
        self.atk_types = [self.atk_type1, self.atke_type2]
        self.atk_ability = self.atk_poke.ability
        self.def_type1 = self.def_poke.type1
        self.def_type2 = self.def_poke.type2    

    def set_type_effectiveness(self):
        self.type_effectiveness = self.calc_type_effectiveness(self.move_type, self.def_type1)
        self.type_effectiveness *= self.calc_type_effectiveness(self.move_type, self.def_type2)

    def set_same_type_factor(self):
        self.same_type_factor = self.calc_same_type_factor(self.move_type, self.atk_types, self.atk_ability)

    def calc_type_effectiveness(self, type1, type2):
        """type1(atk)とtype2(def)のタイプ相性を出力"""
        df_atk_type = df_type[df_type['name'] == type1].copy()
        if type2 == '-':
            #タイプなしの場合(単タイプのタイプ2)、補正なしなので1を戻す。
            return 1
        else:
            factor = self.extract_info(df_atk_type, type2)
            return factor
    
    def calc_same_type_factor(self, move_type, atk_types, atk_ability):
        if move_type in atk_types:
            if atk_ability == 'てきおうりょく':
                return 8192
            else:
                return 6144
        else:
            return 4096

class CalcDamage(OperateDataFrme, CalcCorrectionValue):
    def __init__(
        self,
        move:Move = Move(''), 
        atk_poke:Pokemon =Pokemon(''),
        def_poke:Pokemon =Pokemon(''),
        atk_friend_poke:Pokemon = Pokemon(''),
        def_friend_poke:Pokemon = Pokemon(''),
        atk_item:Item = Item(''),
        def_item:Item = Item(''),
        field:Field = Field(''),
        weather:Weather = Weather(''),
        barrier:Barrier = Barrier(''),
        is_critical:bool = False
    ):
        self.move =move
        self.atk_poke = atk_poke
        self.def_poke = def_poke
        self.atk_friend_poke = atk_friend_poke
        self.def_friend_poke = def_friend_poke
        self.atk_item = atk_item
        self.def_item = def_item
        self.field = field
        self.weather = weather
        self.barrier = barrier
        self.is_critical = is_critical
        self.set_conditions()

    def has_flied(self, pokemon):
        """浮いているポケモンかの判定"""
        if pokemon.type1 == '飛':
            return True
        elif pokemon.type2 == '飛':
            return True
        elif pokemon.ability == 'ふゆう':
            return True
        return False

    def set_conditions(self):
        #ポケモン関連の変数取得
        self.is_dynamax = self.atk_poke.is_dynamax
        self.atk_poke_name = self.atk_poke.name
        self.atk_ability = self.atk_poke.ability
        self.atk_ailment = self.atk_poke.ailment
        self.atk_poke_has_flied = self.has_flied(self.atk_poke)
        self.atk_ability_is_effective = self.atk_poke.is_ability_effective
        self.def_poke_name = self.def_poke.name
        self.def_ability = self.def_poke.ability
        self.def_ailment = self.def_poke.ailment
        self.def_poke_has_flied = self.has_flied(self.def_poke)
        self.def_poke_is_fully_evolved = self.def_poke.is_fully_evolved
        self.atk_friend_ability = self.atk_friend_poke.ability
        self.def_friend_ability = self.def_friend_poke.ability
        #アイテム関連
        self.atk_item_name = self.atk_item.name
        self.def_item_name = self.def_item.name
        if self.def_item =='':
            self.def_has_item = False
        else:
            self.def_has_item = True
        self.def_has_item = self.def_has_item
        #技関連
        self.move_name = self.move.name
        self.move_type = self.move.type
        self.move_category = self.move.category
        self.is_additional_effects = self.move.is_additional_effects
        self.is_biting = self.move.is_biting
        self.is_contact = self.move.is_contact
        self.is_pulse = self.move.is_pulse
        self.is_punching = self.move.is_punching
        self.is_recoil = self.move.is_recoil
        self.is_sound = self.move.is_sound
        self.is_move_effective = self.move.is_effective
        #場の状況関連
        self.field_name = self.field.name
        self.weather_name = self.weather.name
        #タイプ相性関連
        type_factors = TypeCorrection(self.move, self.atk_poke, self.def_poke)
        self.type_effectiveness = type_factors.type_effectiveness
        if self.type_effectiveness >= 2:
            self.is_type_effective = True
        elif self.type_effectiveness <= 0.5:
            self.is_type_effective = False
        else:
            self.is_type_effective = '-'
        self.same_type_factor = type_factors.same_type_factor
        #急所関連
        self.is_critical = self.is_critical

    def select_init_power(self):
        """ダイマックスの有無で威力を出力する。"""
        is_dynamax = self.atk_poke.is_dynamax
        if is_dynamax:
            power = self.move.power_dynamax
        else:
            power = self.move.power
        return power

    def make_last_power_matched_df(self):
        self.set_conditions()
        df_matched_factors = self.make_matched_df(
            df_last_power_factor,
            atk_ability = self.atk_ability,
            atk_friend_ability = self.atk_friend_ability,
            def_ability = self.def_ability,
            atk_item = self.atk_item_name,
            def_has_item = self.def_has_item,
            atk_poke = self.atk_poke_name,
            atk_poke_has_flied = self.atk_poke_has_flied,
            def_poke_has_flied = self.def_poke_has_flied,
            move_name = self.move_name,
            move_type = self.move_type,
            move_category = self.move_category,
            is_additional_effects = self.is_additional_effects,
            is_biting = self.is_biting,
            is_contact = self.is_contact,
            is_pulse = self.is_pulse,
            is_punching = self.is_punching,
            is_recoil = self.is_recoil,
            is_sound = self.is_sound,
            atk_ailment = self.atk_ailment,
            def_ailment = self.def_ailment,
            field_name = self.field_name,
            weather_name = self.weather_name,
            is_ability_effective = self.atk_ability_is_effective,
            is_move_effective = self.is_move_effective,
            is_dynamax = self.is_dynamax
        )
        return df_matched_factors

    def calc_last_power(self):
        power = self.select_init_power()
        if power == 0:
            return 0
        factors = self.make_last_power_matched_df()['factor']
        last_power = power
        last_factor = 4096
        for factor_i in factors:
             last_factor = self.multiply_factor_round4_5(last_factor, factor_i)
        last_power = self.multiply_factor_round5_5(last_power, last_factor)
        if last_power < 1:
            last_power = 1
        return last_power

    def make_last_atk_matched_df(self):
        self.set_conditions()
        df_matched_factors = self.make_matched_df(
            df_last_atk_factor,
            atk_ability = self.atk_ability,
            atk_friend_ability = self.atk_friend_ability,
            def_ability = self.def_ability,
            atk_item = self.atk_item_name,
            atk_poke = self.atk_poke_name,
            move_type = self.move_type,
            atk_ailment = self.atk_ailment,
            weather_name = self.weather_name,
            is_ability_effective = self.atk_ability_is_effective,
            is_dynamax = self.is_dynamax
        )
        return df_matched_factors 

    def calc_last_atk(self):
        last_factor = 4096
        if self.move_category == '物理':
            last_atk = self.atk_poke.status_a
            factors = self.make_last_atk_matched_df()['factor_a']
        else:
            last_atk = self.atk_poke.status_c
            factors = self.make_last_atk_matched_df()['factor_c']
        if self.atk_ability == 'はりきり':
            last_atk = self.multiply_factor_floor(last_atk, 6144)
        for factor_i in factors:
            last_factor = self.multiply_factor_round4_5(last_factor, factor_i)
        last_atk = self.multiply_factor_round5_5(last_atk, last_factor)
        if last_atk < 1:
            last_atk = 1
        return last_atk

    def make_last_def_matched_df(self):
        self.set_conditions()
        df_matched_factors = self.make_matched_df(
            df_last_def_factor,
            def_ability = self.def_ability,
            def_item = self.def_item_name,
            def_poke = self.def_poke_name,
            move_category = self.move_category,
            def_ailment = self.def_ailment,
            field_name = self.field_name,
            is_fully_evolved = self.def_poke_is_fully_evolved
        )
        return df_matched_factors 

    def calc_last_def(self):
        last_factor = 4096
        if self.move_category == '物理':
            last_def = self.def_poke.status_b
            factors = self.make_last_def_matched_df()['factor_b']
        else:
            last_def = self.def_poke.status_d
            factors = self.make_last_def_matched_df()['factor_d']
        if self.weather.name == 'すなあらし':
            if self.def_poke.type1 == '岩' or self.def_poke.type2 == '岩':
                last_def = self.multiply_factor_floor(last_def, 6144)
        for factor_i in factors:
            last_factor = self.multiply_factor_round4_5(last_factor, factor_i)
        last_def = self.multiply_factor_round5_5(last_def, last_factor)
        if last_def < 1:
            last_def = 1
        return last_def
    
    def make_damage_factor_matchef_df(self):
        self.set_conditions()
        df_matched_factors = self.make_matched_df(
            df_damage_factor,
            atk_ability = self.atk_ability,
            def_ability = self.def_ability,
            def_friend_ability = self.def_friend_ability,
            atk_item = self.atk_item_name,
            def_item = self.def_item_name,
            move_name = self.move_name,
            move_type = self.move_type,
            move_category = self.move_category,
            is_contact = self.is_contact,
            is_sound = self.is_sound,
            barrier = self.barrier,
            is_type_effective = self.is_type_effective,
            is_ability_effective = self.atk_ability_is_effective,
            is_move_effective = self.is_move_effective,
            is_critical = self.is_critical,
            is_dynamax = self.is_dynamax
        )
        return df_matched_factors
    
    def calc_damage_factor(self):
        damage_factor = 4096
        factors = self.make_damage_factor_matchef_df()['factor']
        for factor_i in factors:
            damage_factor = self.multiply_factor_round4_5(damage_factor, factor_i)
        return damage_factor

    def calc_damage(self):
        self.set_conditions()
        #各計算値をローカル変数に代入
        last_power = self.calc_last_power()
        #威力が0の場合、0を出力
        if last_power == 0:
            return [0]*16
        last_atk = self.calc_last_atk()
        last_def = self.calc_last_def()
        damage_factor = self.calc_damage_factor()
        #乱数の計算を格納する
        damages =[]

        damage = self.floor(self.atk_poke.level*2/5 + 2)
        damage = self.floor(damage*last_power*last_atk/last_def)
        damage = self.floor(damage/50 + 2)
        #!!範囲技の場合のロジックを考え、if文を追加する。
        #!!範囲技かどうかと、friendがいるかどうかが判定条件
        #!!親子愛の補正を追加する。
        if self.weather_name =='にほんばれ':
            if self.move_type == '炎':
                damage = self.multiply_factor_round5_5(damage, 6144)
            elif self.move_type == '水':
                damage = self.multiply_factor_round5_5(damage, 2048)
        if self.weather_name =='あめ':
            if self.move_type == '水':
                damage = self.multiply_factor_round5_5(damage, 6144)
            elif self.move_type == '炎':
                damage = self.multiply_factor_round5_5(damage, 2048)
        #急所の場合の計算
        if self.is_critical:
            damage = self.multiply_factor_round5_5(damage, 6144)
        #乱数の計算
        for i in range(85, 101):
            damages.append(self.floor(damage*i/100))
        damages = list(map(lambda x: self.multiply_factor_round5_5(x, self.same_type_factor), damages))
        #タイプ相性計算
        if self.move_type == '地' and self.def_poke_has_flied == True:
            self.type_effectiveness = 0
        damages = list(map(lambda x: self.floor(x*self.type_effectiveness), damages))
        if self.atk_ailment == 'やけど' and self.move_category =='物理':
            damages = list(map(lambda x: self.multiply_factor_round5_5(x, 2049), damages))
        damages = list(map(lambda x: self.multiply_factor_round5_5(x, damage_factor), damages))
        #守る補正を記述する
        if damages == [0]*16 and self.type_effectiveness != 0:
            damages = [1]*16
        return damages
