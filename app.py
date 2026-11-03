import streamlit as st
import json
import os
import pandas as pd

# ===================== 账号数据读写工具 =====================
ACCOUNT_FILE = "accounts.json"

def load_accounts():
    """从JSON文件加载所有账号信息"""
    if os.path.exists(ACCOUNT_FILE):
        with open(ACCOUNT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_accounts(accounts_dict):
    """把账号数据保存回JSON文件"""
    with open(ACCOUNT_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts_dict, f, ensure_ascii=False, indent=2)

# ===================== 会话状态初始化 =====================
if "login_status" not in st.session_state:
    st.session_state["login_status"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""
if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""

# ===================== 登录界面 =====================
if not st.session_state["login_status"]:
    st.markdown("## 🏫 七中育才·学生体质健康数据管理系统")
    st.subheader("教师账号登录")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("账号")
        password = st.text_input("密码", type="password")

        if st.button("登录", type="primary", use_container_width=True):
            accounts = load_accounts()
            if username in accounts and accounts[username]["password"] == password:
                st.session_state["login_status"] = True
                st.session_state["current_user"] = username
                st.session_state["user_role"] = accounts[username]["role"]
                st.success("登录成功，正在进入系统...")
                st.rerun()
            else:
                st.error("账号或密码错误，请重试")

# ===================== 登录后主系统 =====================
else:
    # ---------- 侧边栏菜单 ----------
    with st.sidebar:
        st.markdown(f"**当前登录：** {st.session_state['current_user']}")
        role_text = "管理员" if st.session_state["user_role"] == "admin" else "普通教师"
        st.markdown(f"**身份：** {role_text}")
        st.divider()

        # 管理员可见账号管理菜单
        if st.session_state["user_role"] == "admin":
            menu = st.radio("功能菜单", ["系统主页", "账号管理"])
        else:
            menu = st.radio("功能菜单", ["系统主页"])

        st.divider()
        if st.button("退出登录", use_container_width=True):
            st.session_state["login_status"] = False
            st.session_state["current_user"] = ""
            st.session_state["user_role"] = ""
            st.rerun()

    # ========== 菜单1：系统主页（你的原有业务功能） ==========
    if menu == "系统主页":
        st.title("🏫 七中育才·学生体质健康数据管理系统")
        st.divider()

        # --------------------------
        # 原有评分标准（保留你原有的配置）
        # --------------------------
        SCORES = [100, 95, 90, 85, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60, 50, 40, 30, 20, 10]

        # BMI评分标准（依据《国家学生体质健康标准2014》初中段）
        BMI_RULES = {
            # 你可以在这里继续补充完整的BMI评分规则
            "male": {},
            "female": {}
        }

        # ==============================================
        # 👇 下方可以继续编写你原来的所有业务功能代码
        #    比如：数据录入、成绩查询、统计分析、导出报表等
        # ==============================================
        st.info("系统功能区：在此处编写体质数据管理的相关功能")
        
        # 示例：数据上传组件
        st.subheader("学生体质数据导入")
        uploaded_file = st.file_uploader("上传Excel数据文件", type=["xlsx", "xls"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            st.dataframe(df, use_container_width=True)
            st.success("数据导入成功")

    # ========== 菜单2：账号管理（仅管理员可见） ==========
    elif menu == "账号管理" and st.session_state["user_role"] == "admin":
        st.title("⚙️ 教师账号管理")
        accounts = load_accounts()

        # 展示当前账号列表
        st.subheader("当前所有账号")
        account_table = []
        for user, info in accounts.items():
            account_table.append({
                "账号": user,
                "角色": "管理员" if info["role"] == "admin" else "普通教师",
                "密码": info["password"]
            })
        st.dataframe(account_table, use_container_width=True)

        st.divider()

        # 新增教师账号
        st.subheader("新增教师账号")
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("新账号名称")
        with col2:
            new_password = st.text_input("新账号密码", type="password")
        
        if st.button("确认添加账号", type="primary"):
            if not new_username or not new_password:
                st.warning("请填写完整的账号和密码")
            elif new_username in accounts:
                st.error("该账号已存在")
            else:
                accounts[new_username] = {
                    "password": new_password,
                    "role": "teacher"
                }
                save_accounts(accounts)
                st.success(f"账号 {new_username} 添加成功")
                st.rerun()

        st.divider()

        # 删除账号
        st.subheader("删除账号")
        # 过滤掉管理员账号，禁止删除管理员
        delete_list = [u for u in accounts.keys() if accounts[u]["role"] != "admin"]
        if delete_list:
            del_user = st.selectbox("选择要删除的账号", delete_list)
            if st.button("删除选中账号"):
                del accounts[del_user]
                save_accounts(accounts)
                st.success(f"账号 {del_user} 已删除")
                st.rerun()
        else:
            st.info("暂无可删除的教师账号")

        st.divider()

        # 修改密码
        st.subheader("修改账号密码")
        modify_user = st.selectbox("选择要修改的账号", list(accounts.keys()))
        reset_pwd = st.text_input("设置新密码", type="password")
        if st.button("确认修改密码"):
            if not reset_pwd:
                st.warning("请输入新密码")
            else:
                accounts[modify_user]["password"] = reset_pwd
                save_accounts(accounts)
                st.success("密码修改成功")
                st.rerun()

# ===================== 2. 评分标准（与图片完全核对一致） =====================
SCORES = [100, 95, 90, 85, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60, 50, 40, 30, 20, 10]

# BMI评分标准（依据《国家学生体质健康标准2014》初中段）
BMI_RULES = {
    "男生": {"low_weight": 16.5, "normal_high": 23.2, "overweight_high": 26.5},
    "女生": {"low_weight": 16.2, "normal_high": 22.7, "overweight_high": 25.2}
}

# 男生评分标准
BOY_RULES = {
    "初一": {
        "肺活量": {"type": "positive", "values": [3640, 3520, 3400, 3150, 2900, 2780, 2660, 2540, 2420, 2300, 2180, 2060, 1940, 1820, 1700, 1600, 1500, 1400, 1300, 1200]},
        "50米跑": {"type": "negative", "values": [7.8, 7.9, 8.1, 8.3, 8.5, 8.7, 8.9, 9.1, 9.3, 9.5, 9.7, 9.9, 10.1, 10.3, 10.5, 10.7, 10.9, 11.1, 11.3, 11.5]},
        "坐位体前屈": {"type": "positive", "values": [17.6, 15.9, 14.2, 12.3, 10.4, 9.1, 7.8, 6.5, 5.2, 3.9, 2.6, 1.3, 0, -1.3, -2.6, -3.8, -5.0, -6.2, -7.4, -8.6]},
        "立定跳远": {"type": "positive", "values": [225, 218, 211, 203, 195, 191, 187, 183, 179, 175, 171, 167, 163, 159, 155, 150, 145, 140, 135, 130]},
        "引体向上": {"type": "positive", "values": [13, 12, 11, 10, 9, 9, 8, 8, 7, 7, 6, 6, 5, 5, 4, 3, 2, 2, 1, 1]},
        "1000米跑": {"type": "negative", "values": [235, 245, 255, 262, 270, 275, 280, 285, 290, 295, 305, 315, 325, 335, 340, 350, 360, 370, 380, 390]},
    },
    "初二": {
        "肺活量": {"type": "positive", "values": [3940, 3820, 3700, 3450, 3200, 3080, 2960, 2840, 2720, 2600, 2480, 2360, 2240, 2120, 2000, 1890, 1780, 1670, 1560, 1450]},
        "50米跑": {"type": "negative", "values": [7.5, 7.6, 7.7, 7.8, 7.9, 8.1, 8.3, 8.5, 8.7, 8.9, 9.1, 9.3, 9.5, 9.7, 9.9, 10.1, 10.3, 10.5, 10.7, 10.9]},
        "坐位体前屈": {"type": "positive", "values": [19.6, 17.7, 15.8, 13.7, 11.6, 10.3, 9.0, 7.7, 6.4, 5.1, 3.8, 2.5, 1.2, -0.1, -1.4, -2.6, -3.8, -5.0, -6.2, -7.4]},
        "立定跳远": {"type": "positive", "values": [240, 233, 226, 218, 210, 206, 202, 198, 194, 190, 186, 182, 178, 174, 170, 165, 160, 155, 150, 145]},
        "引体向上": {"type": "positive", "values": [14, 13, 12, 11, 10, 10, 9, 9, 8, 8, 7, 7, 6, 6, 5, 4, 3, 3, 2, 2]},
        "1000米跑": {"type": "negative", "values": [230, 240, 250, 257, 265, 270, 275, 280, 285, 290, 300, 310, 320, 330, 335, 345, 355, 365, 375, 385]},
    },
    "初三": {
        "肺活量": {"type": "positive", "values": [4240, 4120, 4000, 3750, 3500, 3380, 3260, 3140, 3020, 2900, 2780, 2660, 2540, 2420, 2300, 2180, 2060, 1940, 1820, 1700]},
        "50米跑": {"type": "negative", "values": [7.3, 7.4, 7.5, 7.6, 7.7, 7.9, 8.1, 8.3, 8.5, 8.7, 8.9, 9.1, 9.3, 9.5, 9.7, 9.9, 10.1, 10.3, 10.5, 10.7]},
        "坐位体前屈": {"type": "positive", "values": [21.6, 19.7, 17.8, 15.3, 12.8, 11.3, 9.8, 8.3, 6.8, 5.3, 3.8, 2.3, 0.8, -0.6, -2.0, -3.2, -4.4, -5.6, -6.8, -8.0]},
        "立定跳远": {"type": "positive", "values": [250, 245, 240, 233, 225, 221, 217, 213, 209, 205, 201, 197, 193, 189, 185, 180, 175, 170, 165, 160]},
        "引体向上": {"type": "positive", "values": [15, 14, 13, 12, 11, 11, 10, 10, 9, 9, 8, 8, 7, 7, 6, 5, 4, 4, 3, 3]},
        "1000米跑": {"type": "negative", "values": [220, 230, 240, 247, 255, 260, 265, 270, 275, 280, 290, 300, 310, 320, 325, 335, 345, 355, 365, 375]},
    }
}

# 女生评分标准
GIRL_RULES = {
    "初一": {
        "肺活量": {"type": "positive", "values": [2750, 2650, 2550, 2450, 2350, 2250, 2150, 2050, 1950, 1850, 1750, 1650, 1550, 1450, 1350, 1310, 1270, 1230, 1190, 1150]},
        "50米跑": {"type": "negative", "values": [8.1, 8.2, 8.3, 8.6, 8.9, 9.1, 9.3, 9.5, 9.7, 9.9, 10.1, 10.3, 10.5, 10.7, 10.9, 11.1, 11.3, 11.5, 11.7, 11.9]},
        "坐位体前屈": {"type": "positive", "values": [21.8, 20.1, 18.4, 16.7, 15.0, 13.9, 12.8, 11.7, 10.6, 9.5, 8.4, 7.3, 6.2, 5.1, 4.0, 2.9, 1.8, 0.7, -0.4, -1.5]},
        "立定跳远": {"type": "positive", "values": [196, 194, 184, 177, 170, 167, 164, 161, 158, 155, 152, 149, 146, 143, 140, 135, 130, 125, 120, 115]},
        "仰卧起坐": {"type": "positive", "values": [50, 48, 47, 43, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10]},
        "800米跑": {"type": "negative", "values": [215, 222, 229, 237, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 295, 305, 315, 325, 335, 345]},
    },
    "初二": {
        "肺活量": {"type": "positive", "values": [2900, 2800, 2650, 2500, 2400, 2300, 2200, 2100, 2000, 1900, 1800, 1700, 1600, 1500, 1400, 1380, 1360, 1340, 1320, 1300]},
        "50米跑": {"type": "negative", "values": [8.0, 8.1, 8.2, 8.5, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8, 10.0, 10.2, 10.4, 10.6, 10.8, 11.0, 11.2, 11.4, 11.6, 11.8]},
        "坐位体前屈": {"type": "positive", "values": [23.7, 22.1, 20.3, 18.6, 16.9, 15.8, 14.7, 13.6, 12.5, 11.4, 10.3, 9.2, 8.1, 7.0, 5.9, 4.8, 3.7, 2.6, 1.5, 0.4]},
        "立定跳远": {"type": "positive", "values": [200, 198, 188, 181, 174, 171, 168, 165, 162, 159, 156, 153, 150, 147, 144, 139, 134, 129, 124, 119]},
        "仰卧起坐": {"type": "positive", "values": [51, 49, 48, 44, 41, 39, 37, 35, 33, 31, 29, 27, 25, 23, 21, 19, 17, 15, 13, 11]},
        "800米跑": {"type": "negative", "values": [210, 217, 224, 232, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 300, 310, 320, 330, 340]},
    },
    "初三": {
        "肺活量": {"type": "positive", "values": [3050, 3000, 2950, 2800, 2650, 2550, 2450, 2350, 2250, 2150, 2050, 1950, 1850, 1750, 1650, 1600, 1550, 1500, 1450, 1400]},
        "50米跑": {"type": "negative", "values": [7.9, 8.0, 8.1, 8.4, 8.7, 8.9, 9.1, 9.3, 9.5, 9.7, 9.9, 10.1, 10.3, 10.5, 10.7, 10.9, 11.1, 11.3, 11.5, 11.7]},
        "坐位体前屈": {"type": "positive", "values": [25.5, 23.8, 22.1, 20.4, 18.7, 17.6, 16.5, 15.4, 14.3, 13.2, 12.1, 11.0, 9.9, 8.8, 7.7, 6.6, 5.5, 4.4, 3.3, 2.2]},
        "立定跳远": {"type": "positive", "values": [202, 200, 190, 183, 176, 173, 170, 167, 164, 161, 158, 155, 152, 149, 146, 141, 136, 131, 126, 121]},
        "仰卧起坐": {"type": "positive", "values": [52, 50, 49, 45, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12]},
        "800米跑": {"type": "negative", "values": [205, 212, 219, 227, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 295, 305, 315, 325, 335]},
    }
}

# 国标权重（满分100分）
WEIGHTS = {
    "BMI": 0.15,
    "肺活量": 0.15,
    "50米跑": 0.20,
    "坐位体前屈": 0.10,
    "立定跳远": 0.10,
    "力量项目": 0.10,
    "耐力跑": 0.20
}

# ===================== 3. 核心算分函数 =====================
def calc_score(grade, gender, item, raw_value):
    """根据年级、性别、项目、原始成绩计算单项得分"""
    if gender == "男生":
        rule_table = BOY_RULES
    else:
        rule_table = GIRL_RULES
    
    if grade not in rule_table or item not in rule_table[grade]:
        return 0
    
    item_rule = rule_table[grade][item]
    values = item_rule["values"]
    score_type = item_rule["type"]

    for i in range(len(SCORES)):
        if score_type == "positive":
            if raw_value >= values[i]:
                return SCORES[i]
        else:
            if raw_value <= values[i]:
                return SCORES[i]
    return SCORES[-1]

def calc_bmi_score(gender, height_cm, weight_kg):
    """计算BMI得分与身体形态等级"""
    if height_cm <= 0 or weight_kg <= 0:
        return 0, 0, "未录入"
    bmi = weight_kg / ((height_cm / 100) ** 2)
    rule = BMI_RULES[gender]
    if bmi < rule["low_weight"]:
        return 80, round(bmi, 1), "低体重"
    elif bmi < rule["normal_high"]:
        return 100, round(bmi, 1), "正常"
    elif bmi < rule["overweight_high"]:
        return 60, round(bmi, 1), "超重"
    else:
        return 50, round(bmi, 1), "肥胖"

def time_to_seconds(time_str):
    """分:秒 转总秒数"""
    try:
        minute, second = str(time_str).split(":")
        return int(minute) * 60 + float(second)
    except:
        return 999

def get_level(total_score):
    """总分判定等级"""
    if total_score >= 90:
        return "优秀"
    elif total_score >= 80:
        return "良好"
    elif total_score >= 60:
        return "及格"
    else:
        return "不及格"

# ===================== 4. 数据本地存储 =====================
DATA_FILE = "fitness_data.csv"
STUDENT_FILE = "student_list.csv"

def load_all_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=[
        "录入时间", "录入教师", "学号", "年级", "班级", "姓名", "性别",
        "身高(cm)", "体重(kg)", "BMI", "BMI等级", "BMI得分",
        "肺活量(ml)", "肺活量得分",
        "50米跑(秒)", "50米跑得分",
        "坐位体前屈(cm)", "坐位体前屈得分",
        "立定跳远(cm)", "立定跳远得分",
        "力量项目", "力量原始成绩", "力量得分",
        "耐力跑项目", "耐力跑原始成绩", "耐力跑得分",
        "总分", "等级"
    ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

def load_student_list():
    """加载学生名单"""
    if os.path.exists(STUDENT_FILE):
        df = pd.read_csv(STUDENT_FILE, dtype={"学号": str})
        return df
    return pd.DataFrame(columns=["学号", "姓名", "年级", "班级", "性别"])

def save_student_list(df):
    """保存学生名单"""
    df.to_csv(STUDENT_FILE, index=False, encoding="utf-8-sig")

# ===================== 5. 批量计算单条成绩（复用函数） =====================
def calc_full_record(record):
    """输入一条原始成绩记录，返回带得分的完整记录"""
    grade = record["年级"]
    gender = record["性别"]
    
    # BMI计算
    bmi_score, bmi_value, bmi_level = calc_bmi_score(gender, record["身高(cm)"], record["体重(kg)"])
    
    # 各单项得分
    score_vc = calc_score(grade, gender, "肺活量", record["肺活量(ml)"])
    score_50m = calc_score(grade, gender, "50米跑", record["50米跑(秒)"])
    score_sr = calc_score(grade, gender, "坐位体前屈", record["坐位体前屈(cm)"])
    score_jump = calc_score(grade, gender, "立定跳远", record["立定跳远(cm)"])
    
    if gender == "男生":
        strength_item = "引体向上"
        endurance_item = "1000米跑"
        score_strength = calc_score(grade, gender, "引体向上", record["力量原始成绩"])
        endurance_sec = time_to_seconds(record["耐力跑原始成绩"])
        score_endurance = calc_score(grade, gender, "1000米跑", endurance_sec)
    else:
        strength_item = "仰卧起坐"
        endurance_item = "800米跑"
        score_strength = calc_score(grade, gender, "仰卧起坐", record["力量原始成绩"])
        endurance_sec = time_to_seconds(record["耐力跑原始成绩"])
        score_endurance = calc_score(grade, gender, "800米跑", endurance_sec)

    # 加权总分
    total = round(
        bmi_score * WEIGHTS["BMI"] +
        score_vc * WEIGHTS["肺活量"] +
        score_50m * WEIGHTS["50米跑"] +
        score_sr * WEIGHTS["坐位体前屈"] +
        score_jump * WEIGHTS["立定跳远"] +
        score_strength * WEIGHTS["力量项目"] +
        score_endurance * WEIGHTS["耐力跑"], 1
    )
    level = get_level(total)

    return {
        "身高(cm)": record["身高(cm)"],
        "体重(kg)": record["体重(kg)"],
        "BMI": bmi_value,
        "BMI等级": bmi_level,
        "BMI得分": bmi_score,
        "肺活量得分": score_vc,
        "50米跑得分": score_50m,
        "坐位体前屈得分": score_sr,
        "立定跳远得分": score_jump,
        "力量项目": strength_item,
        "力量得分": score_strength,
        "耐力跑项目": endurance_item,
        "耐力跑得分": score_endurance,
        "总分": total,
        "等级": level
    }

# ===================== 6. 网页主程序 =====================
def main():
    st.set_page_config(page_title="七中育才体质健康管理系统", layout="wide")
    st.title("🏫 七中育才 · 学生体质健康数据管理系统")

    # 登录状态
    if "is_login" not in st.session_state:
        st.session_state.is_login = False
        st.session_state.username = ""

    # 登录页
    if not st.session_state.get("is_login", False):
        st.subheader("教师账号登录")
        user = st.text_input("账号", key="login_user")
        pwd = st.text_input("密码", type="password", key="login_pwd")
        if st.button("登录", use_container_width=True, type="primary", key="login_submit_btn"):
            if user in USER_ACCOUNTS and USER_ACCOUNTS[user] == pwd:
                st.session_state.is_login = True
                st.session_state.username = user
                st.success("登录成功")
                st.rerun()
            else:
                st.error("账号或密码错误")
        return

    # 侧边栏菜单
    st.sidebar.info(f"当前登录：{st.session_state.username}")
    menu = st.sidebar.radio("功能菜单", [
        "学生名单管理", "成绩录入", "批量导入成绩", "数据查询与导出",
        "学生历史成绩对比", "退出登录"
    ])

    if menu == "退出登录":
        st.session_state.is_login = False
        st.session_state.username = ""
        st.rerun()

    # ---------- 页面0：学生名单管理 ----------
    elif menu == "学生名单管理":
        st.subheader("👥 学生名单管理")
        student_df = load_student_list()

        tab1, tab2, tab3 = st.tabs(["单个添加学生", "批量导入名单", "查看与管理名单"])

        # 单个添加
        with tab1:
            st.write("**添加单个学生信息**")
            col1, col2 = st.columns(2)
            with col1:
                new_id = st.text_input("学号（唯一标识）")
                new_name = st.text_input("学生姓名")
                new_grade = st.selectbox("年级", ["初一", "初二", "初三"])
            with col2:
                new_class = st.text_input("班级", "1班")
                new_gender = st.radio("性别", ["男生", "女生"], horizontal=True)

            if st.button("添加到名单", type="primary"):
                if not new_id.strip() or not new_name.strip():
                    st.warning("请填写学号和姓名")
                elif new_id in student_df["学号"].values:
                    st.warning("该学号已存在，请勿重复添加")
                else:
                    new_row = pd.DataFrame([{
                        "学号": new_id,
                        "姓名": new_name,
                        "年级": new_grade,
                        "班级": new_class,
                        "性别": new_gender
                    }])
                    student_df = pd.concat([student_df, new_row], ignore_index=True)
                    save_student_list(student_df)
                    st.success("添加成功")
                    st.rerun()

        # 批量导入
        with tab2:
            st.write("**第一步：下载模板，按格式填写全班学生名单**")
            template_cols = ["学号", "姓名", "年级", "班级", "性别"]
            template_df = pd.DataFrame(columns=template_cols)
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                template_df.to_excel(writer, index=False, sheet_name="学生名单模板")
            st.download_button(
                label="📄 下载学生名单Excel模板",
                data=buf.getvalue(),
                file_name="学生名单导入模板.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.caption("说明：年级填「初一/初二/初三」，性别填「男生/女生」，学号不能重复")

            st.divider()
            st.write("**第二步：上传填好的Excel文件，批量导入**")
            uploaded_file = st.file_uploader("选择学生名单Excel", type=["xlsx"])
            if uploaded_file is not None:
                try:
                    input_df = pd.read_excel(uploaded_file, dtype={"学号": str})
                    st.write(f"读取到 {len(input_df)} 条学生信息，预览：")
                    st.dataframe(input_df.head(), use_container_width=True)

                    if st.button("确认导入名单", type="primary"):
                        # 去重：学号重复的保留已有
                        exist_ids = set(student_df["学号"].values)
                        new_rows = input_df[~input_df["学号"].isin(exist_ids)]
                        duplicate_count = len(input_df) - len(new_rows)
                        
                        student_df = pd.concat([student_df, new_rows], ignore_index=True)
                        save_student_list(student_df)
                        st.success(f"导入完成：新增 {len(new_rows)} 人，跳过重复学号 {duplicate_count} 人")
                        st.rerun()
                except Exception as e:
                    st.error(f"导入失败：{str(e)}")

        # 查看与管理
        with tab3:
            st.write(f"**当前共有 {len(student_df)} 名学生**")
            # 筛选
            col1, col2 = st.columns(2)
            with col1:
                grade_filter = st.multiselect("按年级筛选", student_df["年级"].unique().tolist(), default=student_df["年级"].unique().tolist())
            with col2:
                class_filter = st.multiselect("按班级筛选", student_df["班级"].unique().tolist(), default=student_df["班级"].unique().tolist())
            
            show_df = student_df[student_df["年级"].isin(grade_filter) & student_df["班级"].isin(class_filter)]
            st.dataframe(show_df, use_container_width=True, height=400)

            # 删除功能
            st.divider()
            st.write("**删除学生（谨慎操作）**")
            del_id = st.text_input("输入要删除的学生学号")
            if st.button("删除该学生", type="secondary"):
                if del_id in student_df["学号"].values:
                    student_df = student_df[student_df["学号"] != del_id]
                    save_student_list(student_df)
                    st.success("删除成功")
                    st.rerun()
                else:
                    st.warning("未找到该学号")

    # ---------- 页面1：单条成绩录入 ----------
    elif menu == "成绩录入":
        st.subheader("📝 学生体测成绩录入")
        student_df = load_student_list()

        if len(student_df) == 0:
            st.warning("⚠️ 暂无学生名单，请先到「学生名单管理」中添加或导入学生信息")
            return

        # 选择学生
        st.subheader("第一步：选择学生")
        # 生成选项：学号 - 姓名
        student_options = [f"{row['学号']} - {row['姓名']}" for _, row in student_df.iterrows()]
        selected = st.selectbox("选择学生（学号-姓名）", student_options)
        selected_id = selected.split(" - ")[0]
        # 获取该学生信息
        student_info = student_df[student_df["学号"] == selected_id].iloc[0]

        # 自动展示基础信息（不可修改）
        col1, col2, col3, col4 = st.columns(4)
        col1.info(f"年级：{student_info['年级']}")
        col2.info(f"班级：{student_info['班级']}")
        col3.info(f"姓名：{student_info['姓名']}")
        col4.info(f"性别：{student_info['性别']}")

        st.divider()
        st.subheader("第二步：录入体测成绩")

        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("身高（厘米）", min_value=0, step=1, value=160)
            weight = st.number_input("体重（公斤）", min_value=0.0, step=0.5, value=50.0)
            vital_capacity = st.number_input("肺活量（毫升）", min_value=0, step=10, value=2500)
            run_50m = st.number_input("50米跑（秒）", min_value=0.0, step=0.1, value=8.5)
        with col2:
            sit_reach = st.number_input("坐位体前屈（厘米）", step=0.1, value=10.0)
            jump = st.number_input("立定跳远（厘米）", min_value=0, step=1, value=180)

        if student_info["性别"] == "男生":
            strength_raw = st.number_input("引体向上（次）", min_value=0, step=1, value=5)
            endurance_str = st.text_input("1000米跑（格式：分:秒，如 4:30）", value="4:30")
        else:
            strength_raw = st.number_input("一分钟仰卧起坐（次）", min_value=0, step=1, value=30)
            endurance_str = st.text_input("800米跑（格式：分:秒，如 3:50）", value="3:50")

        if st.button("计算得分并保存", type="primary", use_container_width=True):
            record = {
                "年级": student_info["年级"], 
                "性别": student_info["性别"],
                "身高(cm)": height, 
                "体重(kg)": weight,
                "肺活量(ml)": vital_capacity,
                "50米跑(秒)": run_50m,
                "坐位体前屈(cm)": sit_reach,
                "立定跳远(cm)": jump,
                "力量原始成绩": strength_raw,
                "耐力跑原始成绩": endurance_str
            }
            result = calc_full_record(record)

            # 展示结果
            st.success("✅ 成绩计算完成")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("BMI得分", f"{result['BMI得分']}分", result["BMI等级"])
            c2.metric("肺活量得分", f"{result['肺活量得分']}分")
            c3.metric("50米跑得分", f"{result['50米跑得分']}分")
            c4.metric("坐位体前屈得分", f"{result['坐位体前屈得分']}分")
            
            c5, c6, c7 = st.columns(3)
            c5.metric("立定跳远得分", f"{result['立定跳远得分']}分")
            c6.metric(f"{result['力量项目']}得分", f"{result['力量得分']}分")
            c7.metric(f"{result['耐力跑项目']}得分", f"{result['耐力跑得分']}分")
            
            st.subheader(f"🎯 总分：{result['总分']} 分 | 等级：{result['等级']}")

            # 保存数据
            df = load_all_data()
            new_row = pd.DataFrame([{
                "录入时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "录入教师": st.session_state.username,
                "学号": student_info["学号"],
                "年级": student_info["年级"], 
                "班级": student_info["班级"],
                "姓名": student_info["姓名"], 
                "性别": student_info["性别"],
                **record, **result
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.info("💾 成绩已保存到系统")

    # ---------- 页面2：批量导入成绩 ----------
    elif menu == "批量导入成绩":
        st.subheader("📥 批量导入成绩")
        
        st.write("**第一步：下载导入模板，按格式填写原始成绩**")
        template_cols = ["学号", "年级", "班级", "姓名", "性别", "身高(cm)", "体重(kg)",
                         "肺活量(ml)", "50米跑(秒)", "坐位体前屈(cm)", "立定跳远(cm)",
                         "力量原始成绩", "耐力跑原始成绩"]
        template_df = pd.DataFrame(columns=template_cols)
        
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            template_df.to_excel(writer, index=False, sheet_name="成绩导入模板")
        st.download_button(
            label="📄 下载Excel导入模板",
            data=buf.getvalue(),
            file_name="体测成绩导入模板.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.caption("说明：男生力量项填引体向上次数，耐力跑填「分:秒」格式（如4:30）；女生同理；建议先导入学生名单，再从名单导出信息粘贴到成绩模板中")

        st.divider()

        st.write("**第二步：上传填好的Excel文件，自动批量算分并保存**")
        uploaded_file = st.file_uploader("选择Excel文件", type=["xlsx"])
        
        if uploaded_file is not None:
            try:
                input_df = pd.read_excel(uploaded_file, dtype={"学号": str})
                st.write(f"共读取到 {len(input_df)} 条记录，预览：")
                st.dataframe(input_df.head(), use_container_width=True)

                if st.button("开始批量计算并导入", type="primary"):
                    df_all = load_all_data()
                    success_count = 0
                    fail_rows = []

                    for idx, row in input_df.iterrows():
                        try:
                            record = {
                                "年级": row["年级"],
                                "性别": row["性别"],
                                "身高(cm)": row["身高(cm)"],
                                "体重(kg)": row["体重(kg)"],
                                "肺活量(ml)": row["肺活量(ml)"],
                                "50米跑(秒)": row["50米跑(秒)"],
                                "坐位体前屈(cm)": row["坐位体前屈(cm)"],
                                "立定跳远(cm)": row["立定跳远(cm)"],
                                "力量原始成绩": row["力量原始成绩"],
                                "耐力跑原始成绩": row["耐力跑原始成绩"]
                            }
                            result = calc_full_record(record)
                            
                            new_row = pd.DataFrame([{
                                "录入时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "录入教师": st.session_state.username,
                                "学号": row.get("学号", ""),
                                "年级": row["年级"],
                                "班级": row["班级"],
                                "姓名": row["姓名"],
                                "性别": row["性别"],
                                **record, **result
                            }])
                            df_all = pd.concat([df_all, new_row], ignore_index=True)
                            success_count += 1
                        except Exception as e:
                            fail_rows.append(f"第{idx+2}行：{str(e)}")

                    save_data(df_all)
                    st.success(f"批量导入完成：成功 {success_count} 条")
                    if fail_rows:
                        st.warning("失败记录：")
                        for f in fail_rows:
                            st.write(f"- {f}")
            except Exception as e:
                st.error(f"文件读取失败，请检查格式：{str(e)}")

    # ---------- 页面3：数据查询与导出 ----------
    elif menu == "数据查询与导出":
        st.subheader("📊 数据查询与 Excel 导出")
        df = load_all_data()

        if len(df) == 0:
            st.info("暂无数据")
            return

        # 筛选
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            grade_filter = st.multiselect("年级", df["年级"].unique().tolist(), default=df["年级"].unique().tolist())
        with col2:
            class_filter = st.multiselect("班级", df["班级"].unique().tolist(), default=df["班级"].unique().tolist())
        with col3:
            gender_filter = st.multiselect("性别", df["性别"].unique().tolist(), default=df["性别"].unique().tolist())
        with col4:
            level_filter = st.multiselect("等级", df["等级"].unique().tolist(), default=df["等级"].unique().tolist())

        result_df = df[
            df["年级"].isin(grade_filter) &
            df["班级"].isin(class_filter) &
            df["性别"].isin(gender_filter) &
            df["等级"].isin(level_filter)
        ]

        st.dataframe(result_df, use_container_width=True, height=400)
        st.caption(f"共 {len(result_df)} 条记录")

        # 统计概览
        if len(result_df) > 0:
            st.subheader("📈 统计概览")
            avg_total = round(result_df["总分"].mean(), 1)
            excellent_rate = round(len(result_df[result_df["等级"]=="优秀"]) / len(result_df) * 100, 1)
            good_rate = round(len(result_df[result_df["等级"]=="良好"]) / len(result_df) * 100, 1)
            pass_rate = round(len(result_df[result_df["等级"].isin(["优秀","良好","及格"])]) / len(result_df) * 100, 1)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("平均分", f"{avg_total} 分")
            c2.metric("优秀率", f"{excellent_rate} %")
            c3.metric("良好率", f"{good_rate} %")
            c4.metric("及格率", f"{pass_rate} %")

            # 导出Excel
            st.divider()
            file_name = f"学生体质健康成绩汇总_{datetime.now().strftime('%Y%m%d')}.xlsx"
            with pd.ExcelWriter("temp_export.xlsx", engine="openpyxl") as writer:
                result_df.to_excel(writer, index=False, sheet_name="成绩明细")
                summary = pd.DataFrame({
                    "指标": ["总人数", "平均分", "优秀率", "良好率", "及格率", "不及格率"],
                    "数值": [len(result_df), avg_total, f"{excellent_rate}%", f"{good_rate}%", f"{pass_rate}%", f"{round(100-pass_rate,1)}%"]
                })
                summary.to_excel(writer, index=False, sheet_name="统计汇总")

            with open("temp_export.xlsx", "rb") as f:
                st.download_button(
                    label="📥 下载 Excel 表格",
                    data=f, file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True, type="primary"
                )

    # ---------- 页面4：学生历史成绩对比 ----------
    elif menu == "学生历史成绩对比":
        st.subheader("📈 学生历史成绩对比分析")
        df = load_all_data()

        if len(df) == 0:
            st.info("暂无数据")
            return

        # 选择学生（按学号+姓名，避免同名）
        student_list = []
        if "学号" in df.columns:
            for _, row in df.drop_duplicates("学号").iterrows():
                student_list.append(f"{row['学号']} - {row['姓名']}")
        else:
            student_list = sorted(df["姓名"].unique().tolist())
        
        selected = st.selectbox("选择学生", student_list)
        
        if "学号" in df.columns:
            selected_id = selected.split(" - ")[0]
            student_data = df[df["学号"] == selected_id].sort_values("录入时间")
        else:
            student_data = df[df["姓名"] == selected].sort_values("录入时间")

        if len(student_data) == 0:
            st.warning("该学生暂无测试记录")
        else:
            st.write(f"**学生信息**：{student_data.iloc[-1]['年级']} {student_data.iloc[-1]['班级']} {student_data.iloc[-1]['性别']}")
            st.write(f"**测试次数**：{len(student_data)} 次")

            # 展示历史记录
            st.dataframe(
                student_data[["录入时间", "年级", "BMI得分", "肺活量得分", "50米跑得分",
                              "坐位体前屈得分", "立定跳远得分", "力量得分", "耐力跑得分", "总分", "等级"]],
                use_container_width=True
            )

            # 前后两次对比
            if len(student_data) >= 2:
                st.divider()
                st.subheader("最新两次成绩对比")
                last = student_data.iloc[-1]
                prev = student_data.iloc[-2]

                compare_df = pd.DataFrame({
                    "项目": ["总分", "BMI得分", "肺活量得分", "50米跑得分",
                            "坐位体前屈得分", "立定跳远得分", "力量得分", "耐力跑得分"],
                    "上次成绩": [prev["总分"], prev["BMI得分"], prev["肺活量得分"], prev["50米跑得分"],
                                prev["坐位体前屈得分"], prev["立定跳远得分"], prev["力量得分"], prev["耐力跑得分"]],
                    "本次成绩": [last["总分"], last["BMI得分"], last["肺活量得分"], last["50米跑得分"],
                                last["坐位体前屈得分"], last["立定跳远得分"], last["力量得分"], last["耐力跑得分"]],
                    "变化值": [
                        round(last["总分"]-prev["总分"],1),
                        last["BMI得分"]-prev["BMI得分"],
                        last["肺活量得分"]-prev["肺活量得分"],
                        last["50米跑得分"]-prev["50米跑得分"],
                        last["坐位体前屈得分"]-prev["坐位体前屈得分"],
                        last["立定跳远得分"]-prev["立定跳远得分"],
                        last["力量得分"]-prev["力量得分"],
                        last["耐力跑得分"]-prev["耐力跑得分"]
                    ]
                })
                st.dataframe(compare_df, use_container_width=True)

                # 薄弱项提示
                weak_items = compare_df[compare_df["变化值"] < 0]["项目"].tolist()
                if weak_items:
                    st.warning(f"⚠️ 退步项目：{ '、'.join(weak_items) }，建议加强针对性训练")
                else:
                    st.success("✅ 所有项目均保持或进步，继续保持")

if __name__ == "__main__":
    main()
