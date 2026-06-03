"""
ALMA Meta広告ダッシュボード 自動更新スクリプト
GitHub Actions で毎朝6時に自動実行される
"""
import os
import json
import urllib.parse
import requests
import pandas as pd
from datetime import datetime

# ==========================================
# 環境変数から認証情報を取得（GitHub Secretsから注入）
# ==========================================
ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
AD_ACCOUNT_ID = "act_1594790327509694"
API_VERSION = "v21.0"
SHEET_ID = "16fV-wGNCrT2cTEKXiGmf8UuShOLWc4B3XXhqdDvlvyQ"

if not ACCESS_TOKEN:
    raise ValueError("META_ACCESS_TOKEN が設定されていません")

# ==========================================
# Step1: スプシから各シートを読み込み
# ==========================================
def read_sheet(sheet_name):
    encoded = urllib.parse.quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded}"
    return pd.read_csv(url)

print("🔄 スプレッドシートからデータ取得中...")

df_route = read_sheet("UTAGE_経路別")
UTAGE_BY_ROUTE = {
    row["登録経路名"]: {"lp_reach": int(row["LP到達"]), "cv": int(row["CV"])}
    for _, row in df_route.iterrows()
}

df_house = read_sheet("UTAGE_ハウス")
UTAGE_HOUSE = {
    "lp_reach": int(df_house["LP到達"].sum()),
    "cv": int(df_house["CV"].sum())
}

df_lp = read_sheet("UTAGE_LP別")
UTAGE_BY_LP = {
    row["LP名"]: {"lp_reach": int(row["LP到達"]), "cv": int(row["CV"]), "cvr": float(row["登録率"])}
    for _, row in df_lp.iterrows()
}

df_config = read_sheet("設定")
config = dict(zip(df_config["項目"], df_config["値"]))
DATE_START = str(config["開始日"])
DATE_END = str(config["終了日"])
GOALS = {
    "target_cpa": int(config["目標CPA"]),
    "target_cv": int(config["目標CV数"]),
    "total_budget": int(config["広告総予算"]),
    "daily_budget": int(config["1日予算"]),
    "campaign_days": int(config["配信期間"]),
    "elapsed_days": int(config["経過日数"]),
}

print(f"  ✅ UTAGE経路別: {len(UTAGE_BY_ROUTE)}件")
print(f"  ✅ UTAGEハウス: CV{UTAGE_HOUSE['cv']}件")
print(f"  ✅ 設定: {DATE_START}〜{DATE_END}")

# ==========================================
# Step2: Meta APIから広告データ取得
# ==========================================
print("\n🔄 Meta APIから広告データ取得中...")

url = f"https://graph.facebook.com/{API_VERSION}/{AD_ACCOUNT_ID}/insights"
params = {
    "fields": "ad_id,ad_name,spend,impressions,clicks,inline_link_clicks,ctr,cpm,cpc",
    "level": "ad",
    "time_range": json.dumps({"since": DATE_START, "until": DATE_END}),
    "limit": 500,
    "access_token": ACCESS_TOKEN
}
resp = requests.get(url, params=params).json()
if "error" in resp:
    raise Exception(f"Meta APIエラー: {resp['error']}")
ads_raw = resp.get("data", [])
print(f"  ✅ {len(ads_raw)}件取得")

# ==========================================
# Step3: クリエイティブ取得
# ==========================================
def get_creative(ad_id):
    try:
        u = f"https://graph.facebook.com/{API_VERSION}/{ad_id}"
        p = {"fields":"creative{image_url,thumbnail_url,title,body,object_story_spec,asset_feed_spec}",
             "access_token": ACCESS_TOKEN}
        r = requests.get(u, params=p).json()
        c = r.get("creative", {})
        image_url = c.get("image_url") or c.get("thumbnail_url", "")
        title = c.get("title", "")
        body = c.get("body", "")
        spec = c.get("object_story_spec", {})
        link = spec.get("link_data", {}) if isinstance(spec, dict) else {}
        if not title:
            title = link.get("name", "") or (link.get("message","")[:30] if link.get("message") else "")
        if not body:
            body = link.get("message", "") or link.get("description", "")
        afs = c.get("asset_feed_spec", {})
        if not title and afs.get("titles"): title = afs["titles"][0].get("text","")
        if not body and afs.get("bodies"): body = afs["bodies"][0].get("text","")
        if not image_url and afs.get("images"): image_url = afs["images"][0].get("url","")
        cta = link.get("call_to_action",{}).get("type","")
        cta_map = {"SIGN_UP":"今すぐ申し込む","LEARN_MORE":"詳しくはこちら","SUBSCRIBE":"登録する"}
        return {"image_url":image_url,"title":title,"body":body,"cta":cta_map.get(cta,"詳細を見る")}
    except:
        return {"image_url":"","title":"","body":"","cta":""}

# ==========================================
# Step4: 判定ロジック
# ==========================================
def judge(spend, cv, ctr, cpa, lp_reach, target_cpa):
    if spend < 100 or lp_reach < 10:
        return ("データ不足","v-na","消化金額やLP到達が少なく判断不可","配信開始または消化量を増やす")
    cvr = (cv/lp_reach*100) if lp_reach>0 else 0
    if cv >= 1 and cpa is not None and cpa <= target_cpa and cvr >= 3:
        return ("寄せる","v-scale","CPAが目標以下、CVあり、登録率が平均以上","予算を増やして配信を拡大")
    if cv >= 1 and cpa is not None and cpa <= target_cpa * 1.5:
        return ("継続","v-keep","CVあり、CPAが許容範囲内","現状維持で配信を続ける")
    if ctr >= 5.0 and cv == 0:
        return ("要改善","v-improve","CTRは高いが登録率が低い、LPやフォームに課題","LP・フォームを見直す")
    if spend >= 1000 and cv == 0:
        return ("停止候補","v-stop","消化あり、CVなし、CTRも低い","停止または訴求の大幅変更")
    if spend >= 500 and cv == 0 and ctr < 3.0:
        return ("停止候補","v-stop","消化あり、CVなし、CTRも低い","停止または訴求の大幅変更")
    return ("様子見","v-watch","クリックやLP到達はあるが、CV数がまだ少ない","もう少しデータを蓄積")

# ==========================================
# Step5: 広告処理
# ==========================================
ads_processed = []
for ad in ads_raw:
    name = ad.get("ad_name","")
    spend = float(ad.get("spend",0))
    imp = int(ad.get("impressions",0))
    clicks = int(ad.get("clicks",0))
    lc = int(ad.get("inline_link_clicks",0))
    ctr = float(ad.get("ctr",0))
    cpm = float(ad.get("cpm",0))
    cpc = float(ad.get("cpc",0))
    u = UTAGE_BY_ROUTE.get(name, {"lp_reach":0,"cv":0})
    lp = u["lp_reach"]; cv = u["cv"]
    cvr = round(cv/lp*100,2) if lp>0 else 0
    cpa = round(spend/cv) if cv>0 else None
    verdict, vclass, reason, next_action = judge(spend, cv, ctr, cpa, lp, GOALS["target_cpa"])
    ads_processed.append({
        "name":name,"spend":round(spend),"impressions":imp,"clicks":clicks,"link_clicks":lc,
        "ctr":round(ctr,2),"cpc":round(cpc),"cpm":round(cpm),
        "lp_reach":lp,"cv":cv,"cvr":cvr,"cpa":cpa,
        "verdict":verdict,"verdict_class":vclass,"reason":reason,"next_action":next_action,
        "appeal":"—","strength":"—","concern":"—","improvement":"—","expansion":"—",
        "creative": get_creative(ad["ad_id"])
    })

# ==========================================
# Step6: 集計・data.json構築
# ==========================================
total_spend = sum(a["spend"] for a in ads_processed)
total_imp = sum(a["impressions"] for a in ads_processed)
total_clicks = sum(a["clicks"] for a in ads_processed)
total_lc = sum(a["link_clicks"] for a in ads_processed)
total_ctr = round(total_lc/total_imp*100,2) if total_imp>0 else 0
ad_lp = sum(a["lp_reach"] for a in ads_processed)
ad_cv = sum(a["cv"] for a in ads_processed)
ad_cvr = round(ad_cv/ad_lp*100,2) if ad_lp>0 else 0
ad_cpa = round(total_spend/ad_cv) if ad_cv>0 else None
house_lp = UTAGE_HOUSE["lp_reach"]; house_cv = UTAGE_HOUSE["cv"]
house_cvr = round(house_cv/house_lp*100,2) if house_lp>0 else 0
total_cv = ad_cv + house_cv
total_lp = ad_lp + house_lp
total_cvr = round(total_cv/total_lp*100,2) if total_lp>0 else 0
ad_contrib = round(ad_cv/total_cv*100,1) if total_cv>0 else 0
house_contrib = round(house_cv/total_cv*100,1) if total_cv>0 else 0

cpa_status = "good" if ad_cpa is not None and ad_cpa <= GOALS["target_cpa"] else "warn"
cv_progress = round(total_cv/GOALS["target_cv"]*100,1) if GOALS["target_cv"]>0 else 0
budget_used = round(total_spend/GOALS["total_budget"]*100,1) if GOALS["total_budget"]>0 else 0
remaining_days = GOALS["campaign_days"] - GOALS["elapsed_days"]
expected_total_cv = round(total_cv/GOALS["elapsed_days"]*GOALS["campaign_days"]) if GOALS["elapsed_days"]>0 else 0
forecast_status = "good" if expected_total_cv >= GOALS["target_cv"] else "warn"

if ad_cpa is None: eval_status, eval_class = "データ不足","eval-na"
elif ad_cpa <= GOALS["target_cpa"] and cv_progress >= 30 and ad_cv > 0:
    eval_status, eval_class = "良好","eval-good"
elif ad_cpa <= GOALS["target_cpa"]*1.5 and ad_cv > 0:
    eval_status, eval_class = "注意","eval-warn"
else:
    eval_status, eval_class = "改善必要","eval-bad"

parts = []
if ad_cpa is not None:
    if ad_cpa <= GOALS["target_cpa"]:
        parts.append(f"広告経由CPAは¥{ad_cpa:,}で推移しており、目標CPA¥{GOALS['target_cpa']:,}以内で良好です。")
    else:
        parts.append(f"広告経由CPAは¥{ad_cpa:,}で、目標CPA¥{GOALS['target_cpa']:,}を超過しています。")
parts.append(f"CVは広告経由{ad_cv}件、ハウスリスト{house_cv}件、合計{total_cv}件を獲得しました。")
parts.append(f"目標CV{GOALS['target_cv']}件に対して{cv_progress}%進捗、予算消化率は{budget_used}%です。")
situation = " ".join(parts)

next_actions = []
scale_ads = [a["name"] for a in ads_processed if a["verdict"]=="寄せる"]
if scale_ads: next_actions.append(f"予算を寄せる：{', '.join(scale_ads)}")
stop_ads = [a["name"] for a in ads_processed if a["verdict"]=="停止候補"]
if stop_ads: next_actions.append(f"停止または訴求変更を検討：{', '.join(stop_ads)}")
imp_ads = [a["name"] for a in ads_processed if a["verdict"]=="要改善"]
if imp_ads: next_actions.append(f"LP・フォームを見直す：{', '.join(imp_ads)}")

data = {
    "_meta": {"title":"ALMA Meta広告 ダッシュボード","client_name":"アルマ・クリエイション株式会社",
              "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
              "data_sources":{"ads_metrics":"Meta Marketing API","cv_and_lp_reach":"UTAGE登録経路別（スプシ連携）"}},
    "report_period": {"start_date":DATE_START,"end_date":DATE_END,
                      "campaign_days":GOALS["campaign_days"],"elapsed_days":GOALS["elapsed_days"],
                      "remaining_days":remaining_days},
    "overall_evaluation": {"status":eval_status,"status_class":eval_class,
                           "comment":situation,"next_actions":next_actions},
    "goals": {"target_cpa":GOALS["target_cpa"],"target_cv":GOALS["target_cv"],
              "total_budget":GOALS["total_budget"],"daily_budget":GOALS["daily_budget"],
              "current_cpa":ad_cpa,"current_cv":total_cv,"current_spend":total_spend,
              "cpa_status":cpa_status,"cv_progress":cv_progress,"budget_used":budget_used,
              "expected_total_cv":expected_total_cv,"forecast_status":forecast_status},
    "channel_summary": {"total_cv":total_cv,"ad_cv":ad_cv,"house_cv":house_cv,
                        "ad_contribution_rate":ad_contrib,"house_contribution_rate":house_contrib},
    "channels": {
        "overall":{"label":"全体","description":"プロモーション全体の申込状況を見るエリア（広告＋ハウスリスト合算）",
                   "kpis":{"total_spend":total_spend,"total_cv":total_cv,
                           "total_lp_reach":total_lp,"overall_cvr":total_cvr}},
        "ad":{"label":"広告経由","description":"新規集客の獲得効率を見るエリア（Meta広告経由のCVと費用対効果）",
              "kpis":{"spend":total_spend,"impressions":total_imp,"clicks":total_clicks,
                      "link_clicks":total_lc,"ctr":total_ctr,"lp_reach":ad_lp,
                      "cv":ad_cv,"cvr":ad_cvr,"cpa":ad_cpa}},
        "house":{"label":"ハウスリスト","description":"既存リストの温度感・反応率を見るエリア（メルマガ・ステップメール経由）",
                 "kpis":{"lp_reach":house_lp,"cv":house_cv,"cvr":house_cvr}}
    },
    "funnel": {
        "stages":[
            {"label":"インプレッション","value":total_imp,"rate":None},
            {"label":"クリック","value":total_clicks,
             "rate":round(total_clicks/total_imp*100,2) if total_imp>0 else 0,"rate_label":"CTR"},
            {"label":"LP到達","value":ad_lp,
             "rate":round(ad_lp/total_clicks*100,2) if total_clicks>0 else 0,"rate_label":"LP到達率"},
            {"label":"申込完了","value":ad_cv,
             "rate":round(ad_cv/ad_lp*100,2) if ad_lp>0 else 0,"rate_label":"登録率"}],
        "insights":["クリック率が低い → 広告クリエイティブやコピーの問題",
                    "LP到達率が低い → ピクセル計測のタイミングや読み込み速度の問題",
                    "登録率が低い → LP訴求やフォーム入力負荷の問題"]
    },
    "ads_performance": ads_processed,
    "lp_performance": [
        {"name":k,**v,"verdict":("勝ち" if v["cvr"]>=10 else ("データ不足" if v["lp_reach"]<10 else "並")),
         "comment":("登録率が高く最優秀。配信を寄せる" if v["cvr"]>=10 else
                    ("アクセスがほぼなく判断不可" if v["lp_reach"]<10 else "標準的なLP。改善余地あり"))}
        for k,v in UTAGE_BY_LP.items()
    ],
    "client_comments": {
        "today_summary":"（運用者が記入）本日のまとめ",
        "good_points":"（運用者が記入）良かった点",
        "concerns":"（運用者が記入）懸念点",
        "next_todo":"（運用者が記入）次にやること",
        "client_questions":"（運用者が記入）クライアントへの確認事項"
    }
}

with open("data.json","w",encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n✅ data.json 生成完了")
print(f"総合評価: {eval_status} / CPA¥{ad_cpa} / CV{total_cv}件")
