# ダメージ感覚ツール(仮称)
被ダメージや与ダメージから相手ポケモンのステータスや持ち物を推定するツール。  
機能としてはステータスやアイテムの推測だが、ポケモン対戦勢になじみある用語**ダメ感**をツール名に着けたいと思い命名。

## やりたいこと
対戦時の明らかな情報とダメージ量から、明らかでない情報をダメージ計算結果から推定する。  
明らかな情報をインプット。明らかでない情報は全パターンインプット。その計算結果とダメージ量を比較することで推定できるはず。  
明らかor明らかでない情報は状況によって変わるが以下の3パターンで分類できそう。

|攻撃サイド|ダイマックス|パターン|
|----|----|----|
|自分|Yes|1|
|自分|No|1|
|相手|Yes|2|
|相手|No|3|

## 各パターンでの情報分類
各パターンでダメ計に必要な値のうち何が明らかかを箇条書き。  
基本的には相手のポケモン能力値、アイテム、特性がわからない。相手がダイマックスする場合は、技の威力やカテゴリが不明になる。
### パターン1(自分が攻撃側)
#### 明らかな情報
- 攻撃側(自分)の全情報
- フィールド
- 天候
- 壁
- HP変化割合(おおよそ)
#### 明らかでない情報
- 防御側の個体値、努力値
- 防御側の性格
- 防御側のアイテム
- 防御側のとくせい
### パターン2(相手が攻撃側でダイマックス)
#### 明らかな情報
- 防御側(自分)の全情報
- フィールド
- 天候
- 壁
- ダメージ量
#### 明らかでない情報
- 攻撃側の個体値、努力値
- 攻撃側の性格
- 攻撃側のアイテム
- 攻撃側のとくせい
- **攻撃側の技詳細(威力など)**
### パターン3(相手が攻撃側で通常状態)
#### 明らかな情報
- 防御側(自分)の全情報
- フィールド
- 天候
- 壁
- **攻撃側のわざ**
- ダメージ量
#### 明らかでない情報
- 攻撃側の個体値、努力値
- 攻撃側の性格
- 攻撃側のアイテム
- 攻撃側のとくせい

## フローチャート
パターン1についてフローチャートを考えた。その他パターンも似たフローになるはず。
``` mermaid
graph TD
	oMyInfo["自分情報<br>ステータス、攻撃技"]
	oCondition["場の状況"]
	oEneIV["相手BorD個体値<br>0-31(32種類)"]
	oEneEV["相手BorD努力値<br>0-252(33種類)"]
	oEneNat["相手性格補正<br>(3種類)"]
	oEneStat["相手ステータス<br>(最大値~最低値の約80種類)"]
	oEneAbi["相手とくせい<br>(max3種類)"]
	oEneItm["相手アイテム<br>(x種類)"]
	oEneInfo["相手情報一覧"]
	oDam["ダメージ量"]
	oDamRsl["ダメージ計算結果"]
	oMoveType["攻撃技カテゴリ"]
	oSearchRslt["一致した条件"]
	oSearchedInfo["相手情報詳細<br>個体値、努力値、性格、アイテム、特性"]
	

	subgraph 明らかな情報
		oMyInfo
		oCondition
		oMoveType
		oDam
	end
	subgraph 明らかでない情報
		oEneIV
		oEneEV
		oEneNat
		oEneAbi
		oEneItm
		oEneStat
	end
	fCalcStat(ステータス計算)
	fCrossJoin(クロスジョイン)
	fCalcDamage(ダメ計)
	fCompare(比較)
	fReverseCalcStatus(逆ステータス計算)

	ifAbility{相手特性でダメ計に違いが出るか}

	oEneAbi --> ifAbility
	oMyInfo --> oMoveType
	 oMoveType & oEneIV & oEneEV & oEneNat -->fCalcStat --> oEneStat

	oEneStat  & oEneItm --> fCrossJoin --> oEneInfo
	ifAbility -->|yes| fCrossJoin

	oCondition & oMyInfo & oEneInfo --> fCalcDamage -->oDamRsl

	oDam & oDamRsl --> fCompare --> oSearchRslt -->fReverseCalcStatus --> oSearchedInfo
```

ダメ計～比較のフローチャート
```mermaid
graph TD
	start[開始]
	status_list["推定ステータスリスト"]
	add_status_list("ステータスリストに追加する")
	calc_max_min("ステータスの最大値最小値を計算する")
	status["ステータス(max)"]
	ini_flag["初期フラグ=False<br>計算範囲内か"]
	calc_damage("ダメージ計算する")
	check_damage{"ダメージが計算内か確認"}
	flag_change(フラグをFalseからyesに変更)
	check_flag{"フラグをチェックする"}
	check_flag2{"フラグをチェックする"}
	check_status{"ステータスが最小か"}
	change_status("ステータスを-1する")
	other_item{"ほかのアイテムがあるか"}
	item["アイテムを選択"]
	stop["停止"]

	start --> item --> calc_damage
	start --> ini_flag --> check_damage
	start --> calc_max_min
	calc_max_min --> status --> calc_damage --> check_damage
	check_damage -->|True| add_status_list --> check_flag
	add_status_list -.-> status_list
	check_damage -->|False| check_flag2
	check_flag -->|True| check_status -->|False| change_status --> calc_damage
	check_flag -->|False| flag_change -->check_status
	check_status -->|True| other_item
	other_item -->|True| item
	other_item -->|False| stop
	status_list --> stop

	check_flag2 -->|True| other_item
	check_flag2 -->|False| check_status
```