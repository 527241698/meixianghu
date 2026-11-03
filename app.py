import streamlit as st
import pandas as pd
import json
import os
from io import BytesIO

# =====================
# 1. 国家体质健康评分标准（严格对照图片核对）
# =====================
# 说明：标准按「得分, 初一, 初二, 初三」格式存储
# 项目类型：higher_better=数值越⼤分越⾼；lower_better=数值越⼩分越⾼

# ---------- 男生评分标准 ----------
# 肺活量（ml）- 越大越好
MALE_VITAL = [
    (100, 3640, 3940, 4240), (95, 3520, 3820, 4120), (90, 3400, 3700, 4000),
    (85, 3150, 3450, 3750), (80, 2900, 3200, 3500), (78, 2780, 3080, 3380),
    (76, 2660, 2960, 3260), (74, 2540, 2840, 3140), (72, 2420, 2720, 3020),
    (70, 2300, 2600, 2900), (68, 2180, 2480, 2780), (66, 2060, 2360, 2660),
    (64, 1940, 2240, 2540), (62, 1820, 2120, 2420), (60, 1700, 2000, 2300),
    (50, 1600, 1890, 2180), (40, 1500, 1780, 2060), (30, 1400, 1670, 1940),
    (20, 1300, 1560, 1820), (10, 1200, 1450, 1700)
]

# 50米跑（秒）- 越小越好
MALE_RUN50 = [
    (100, 7.8, 7.5, 7.3), (95, 7.9, 7.6, 7.4), (90, 8.0, 7.7, 7.5),
    (85, 8.1, 7.8, 7.6), (80, 8.2, 7.9, 7.7), (78, 8.4, 8.1, 7.9),
    (76, 8.6, 8.3, 8.1), (74, 8.8, 8.5, 8.3), (72, 9.0, 8.7, 8.5),
    (70, 9.2, 8.9, 8.7), (68, 9.4, 9.1, 8.9), (66, 9.6, 9.3, 9.1),
    (64, 9.8, 9.5, 9.3), (62, 10.0, 9.7, 9.5), (60, 10.2, 9.9, 9.7),
    (50, 10.4, 10.1, 9.9), (40, 10.6, 10.3, 10.1), (30, 10.8, 10.5, 10.3),
    (20, 11.0, 10.7, 10.5), (10, 11.2, 10.9, 10.7)
]

# 坐位体前屈（cm）- 越大越好
MALE_SIT_REACH = [
    (100, 17.6, 19.6, 21.6), (95, 15.9, 17.7, 19.7), (90, 14.2, 15.8, 17.8),
    (85, 12.3, 13.7, 15.3), (80, 10.4, 11.6, 13.8), (78, 9.1, 10.3, 12.4),
    (76, 7.8, 9.0, 11.0), (74, 6.5, 7.7, 9.6), (72, 5.2, 6.4, 8.2),
    (70, 3.9, 5.1, 6.8), (68, 2.6, 3.8, 5.4), (66, 1.3, 2.5, 4.0),
    (64, 0.0, 1.2, 2.6), (62, -1.3, -0.1, 1.2), (60, -2.6, -1.4, -0.2),
    (50, -3.8, -2.6, -1.4), (40, -5.0, -3.8, -2.6), (30, -6.2, -5.0, -3.8),
    (20, -7.4, -6.2, -5.0), (10, -8.6, -7.4, -6.2)
]

# 立定跳远（cm）- 越大越好
MALE_JUMP = [
    (100, 225, 240, 250), (95, 218, 233, 245), (90, 211, 226, 240),
    (85, 203, 218, 233), (80, 195, 210, 225), (78, 191, 206, 221),
    (76, 187, 202, 217), (74, 183, 198, 213), (72, 179, 194, 209),
    (70, 175, 190, 205), (68, 171, 186, 201), (66, 167, 182, 197),
    (64, 163, 178, 193), (62, 159, 174, 189), (60, 155, 170, 185),
    (50, 150, 165, 180), (40, 145, 160, 175), (30, 140, 155, 170),
    (20, 135, 150, 165), (10, 130, 145, 160)
]

# 引体向上（次）- 越大越好
MALE_PULLUP = [
    (100, 13, 14, 15), (95, 12, 13, 14), (90, 11, 12, 13),
    (85, 10, 11, 12), (80, 9, 10, 11), (78, 9, 10, 11),
    (76, 8, 9, 10), (74, 8, 9, 10), (72, 7, 8, 9),
    (70, 7, 8, 9), (68, 6, 7, 8), (66, 6, 7, 8),
    (64, 5, 6, 7), (62, 5, 6, 7), (60, 4, 5, 6),
    (50, 3, 4, 5), (40, 2, 3, 4), (30, 1, 2, 3),
    (20, 1, 1, 2), (10, 1, 1, 1)
]

# 1000米跑（秒）- 越小越好（已转换为总秒数）
MALE_RUN1000 = [
    (100, 235, 230, 220), (95, 245, 235, 225), (90, 255, 240, 230),
    (85, 262, 247, 237), (80, 270, 255, 245), (78, 275, 260, 250),
    (76, 280, 265, 255), (74, 285, 270, 260), (72, 290, 275, 265),
    (70, 295, 280, 270), (68, 300, 285, 275), (66, 305, 290, 280),
    (64, 310, 295, 285), (62, 315, 300, 290), (60, 320, 305, 295),
    (50, 340, 325, 315), (40, 360, 345, 335), (30, 380, 365, 355),
    (20, 400, 385, 375), (10, 420, 405, 395)
]

# ---------- 女生评分标准 ----------
# 肺活量（ml）- 越大越好
FEMALE_VITAL = [
    (100, 2750, 2900, 3050), (95, 2650, 2800, 3000), (90, 2550, 2700, 2950),
    (85, 2450, 2650, 2800), (80, 2350, 2500, 2650), (78, 2250, 2400, 2550),
    (76, 2150, 2300, 2450), (74, 2050, 2200, 2350), (72, 1950, 2100, 2250),
    (70, 1850, 2000, 2150), (68, 1750, 1900, 2050), (66, 1650, 1800, 1950),
    (64, 1550, 1700, 1850), (62, 1450, 1600, 1750), (60, 1350, 1500, 1650),
    (50, 1310, 1460, 1610), (40, 1270, 1420, 1570), (30, 1230, 1380, 1530),
    (20, 1190, 1340, 1490), (10, 1150, 1300, 1450)
]

# 50米跑（秒）- 越小越好
FEMALE_RUN50 = [
    (100, 8.1, 7.9, 7.8), (95, 8.2, 8.1, 7.9), (90, 8.3, 8.2, 8.1),
    (85, 8.6, 8.5, 8.4), (80, 8.9, 8.8, 8.7), (78, 9.1, 9.0, 8.9),
    (76, 9.3, 9.2, 9.1), (74, 9.5, 9.4, 9.3), (72, 9.7, 9.6, 9.5),
    (70, 9.9, 9.8, 9.7), (68, 10.1, 10.0, 9.9), (66, 10.3, 10.2, 10.1),
    (64, 10.5, 10.4, 10.3), (62, 10.7, 10.6, 10.5), (60, 10.9, 10.8, 10.7),
    (50, 11.1, 11.0, 10.9), (40, 11.3, 11.2, 11.1), (30, 11.5, 11.4, 11.3),
    (20, 11.7, 11.6, 11.5), (10, 11.9, 11.8, 11.7)
]

# 坐位体前屈（cm）- 越大越好
FEMALE_SIT_REACH = [
    (100, 21.8, 22.7, 23.5), (95, 20.1, 21.0, 21.8), (90, 18.4, 19.3, 20.1),
    (85, 16.7, 17.6, 18.4), (80, 15.0, 15.9, 16.7), (78, 13.7, 14.6, 15.4),
    (76, 12.4, 13.3, 14.1), (74, 11.1, 12.0, 12.8), (72, 9.8, 10.7, 11.5),
    (70, 8.5, 9.4, 10.2), (68, 7.2, 8.1, 8.9), (66, 5.9, 6.8, 7.6),
    (64, 4.6, 5.5, 6.3), (62, 3.3, 4.2, 5.0), (60, 2.0, 2.9, 3.7),
    (50, 1.2, 2.1, 2.9), (40, 0.4, 1.3, 2.1), (30, -0.4, 0.5, 1.3),
    (20, -1.2, -0.3, 0.5), (10, -2.0, -1.1, -0.3)
]

# 立定跳远（cm）- 越大越好
FEMALE_JUMP = [
    (100, 196, 202, 202), (95, 190, 196, 196), (90, 184, 188, 190),
    (85, 177, 181, 184), (80, 170, 174, 176), (78, 167, 171, 173),
    (76, 164, 168, 170), (74, 161, 165, 167), (72, 158, 162, 164),
    (70, 155, 159, 161), (68, 152, 156, 158), (66, 149, 153, 155),
    (64, 146, 150, 152), (62, 143, 147, 149), (60, 140, 144, 146),
    (50, 135, 139, 141), (40, 130, 134, 136), (30, 125, 129, 131),
    (20, 120, 124, 126), (10, 115, 119, 121)
]

# 一分钟仰卧起坐（次）- 越大越好
FEMALE_SITUP = [
    (100, 50, 51, 52), (95, 48, 49, 50), (90, 47, 48, 49),
    (85, 43, 44, 45), (80, 40, 41, 42), (78, 38, 39, 40),
    (76, 36, 37, 38), (74, 34, 35, 36), (72, 32, 33, 34),
    (70, 30, 31, 32), (68, 28, 29, 30), (66, 26, 27, 28),
    (64, 24, 25, 26), (62, 22, 23, 24), (60, 20, 21, 22),
    (50, 18, 19, 20), (40, 16, 17, 18), (30, 14, 15, 16),
    (20, 12, 13, 14), (10, 10, 11, 12)
]

# 800米跑（秒）- 越小越好（已转换为总秒数）
FEMALE_RUN800 = [
    (100, 215, 210, 205), (95, 222, 217, 212), (90, 229, 224, 219),
    (85, 239, 234, 227), (80, 245, 240, 235), (78, 250, 245, 240),
    (76, 255, 250, 245), (74, 260, 255, 250), (72, 265, 260, 255),
    (70, 270, 265, 260), (68, 275, 270, 265), (66, 280, 275, 270),
    (64, 285, 280, 275), (62, 290, 285, 280), (60, 295, 290, 285),
    (50, 305, 300, 295), (40, 315, 310, 305), (30, 325, 320, 315),
    (20, 335, 330, 325), (10, 345, 340, 335)
]

# 年级索引映射
GRADE_INDEX = {"初一": 1, "初二": 2, "初三": 3}

# =====================
# 2. 评分核心函数
# =====================
def calc_score(standard_list, value, grade, higher_better=True):
    """
    根据评分标准计算单项得分（支持线性插值）
    :param standard_list: 评分标准列表
    :param value: 学生成绩
    :param grade: 年级（初一/初二/初三）
    :param higher_better: 是否数值越大分越高
    :return: 得分（保留1位小数）
    """
    idx = GRADE_INDEX[grade]
    scores = [item[0] for item in standard_list]
    values = [item[idx] for item in standard_list]

    # 边界处理
    if higher_better:
        if value >= values[0]:
            return 100.0
        if value <= values[-1]:
            return 10.0
    else:
        if value <= values[0]:
            return 100.0
        if value >= values[-1]:
            return 10.0

    # 查找区间并线性插值
    for i in range(len(values) - 1):
        v_high, v_low = values[i], values[i+1]
        s_high, s_low = scores[i], scores[i+1]

        if higher_better:
            if v_low <= value <= v_high:
                ratio = (value - v_low) / (v_high - v_low)
                return round(s_low + ratio * (s_high - s_low), 1)
        else:
            if v_high <= value <= v_low:
                ratio = (v_low - value) / (v_low - v_high)
                return round(s_low + ratio * (s_high - s_low), 1)
    return 0.0

def get_level(total_score):
    """根据总分判定等级"""
    if total_score >= 90:
        return "优秀"
    elif total_score >= 80:
        return "良好"
    elif total_score >= 60:
        return "合格"
    else:
        return "不及格"

def time_to_seconds(minutes, seconds):
    """分:秒 转总秒数"""
    return minutes * 60 + seconds

# =====================
# 3. 常量与数据读写工具
# =====================
ACCOUNT_FILE = "accounts.json"
STUDENT_FILE = "students.csv"
SCORE_FILE = "scores.csv"

def load_accounts():
    if os.path.exists(ACCOUNT_FILE):
        with open(ACCOUNT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"teacher1": "123456", "admin": "admin123"}

def save_students(df):
    df.to_csv(STUDENT_FILE, index=False, encoding="utf-8-sig")

def load_students():
    if os.path.exists(STUDENT_FILE):
        return pd.read_csv(STUDENT_FILE, dtype={"学号": str})
    return pd.DataFrame(columns=["学号", "姓名", "性别", "年级", "班级"])

def save_scores(df):
    df.to_csv(SCORE_FILE, index=False, encoding="utf-8-sig")

def load_scores():
    cols = [
        "学号", "姓名", "性别", "年级", "班级", "测试学期",
        "身高(cm)", "体重(kg)", "肺活量(ml)", "肺活量得分",
        "50米跑(s)", "50米跑得分",
        "坐位体前屈(cm)", "坐位体前屈得分",
        "立定跳远(cm)", "立定跳远得分",
        "力量项目成绩", "力量项目得分",
        "耐力跑(秒)", "耐力跑得分",
        "总分", "等级"
    ]
    if os.path.exists(SCORE_FILE):
        return pd.read_csv(SCORE_FILE, dtype={"学号": str})
    return pd.DataFrame(columns=cols)

# =====================
# 4. 页面全局初始化
# =====================
st.set_page_config(
    page_title="七中育才·学生体质健康数据管理系统",
    layout="wide"
)

if "is_login" not in st.session_state:
    st.session_state.is_login = False
    st.session_state.username = ""

if "students_df" not in st.session_state:
    st.session_state.students_df = load_students()
if "scores_df" not in st.session_state:
    st.session_state.scores_df = load_scores()

USER_ACCOUNTS = load_accounts()

# =====================
# 5. 登录页逻辑
# =====================
if not st.session_state.is_login:
    st.markdown("# 🏫 七中育才·学生体质健康数据管理系统")
    st.divider()
    st.subheader("教师账号登录")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
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
    st.stop()

# =====================
# 6. 侧边栏菜单
# =====================
st.sidebar.info(f"当前登录：{st.session_state.username}")
st.sidebar.text("身份：普通教师")
st.sidebar.divider()

menu = st.sidebar.radio(
    "功能菜单",
    [
        "系统主页",
        "学生信息管理",
        "体质成绩录入",
        "成绩查询与导出",
        "学生历史成绩对比"
    ]
)

st.sidebar.divider()
if st.sidebar.button("退出登录", use_container_width=True, key="logout_btn"):
    st.session_state.is_login = False
    st.session_state.username = ""
    st.rerun()

# =====================
# 7. 各功能页面实现
# =====================

# ---------- 系统主页 ----------
if menu == "系统主页":
    st.title("🏫 七中育才·学生体质健康数据管理系统")
    st.divider()
    st.info("系统已集成国家学生体质健康标准，支持自动评分、等级判定、达标统计")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("在册学生数", len(st.session_state.students_df))
    col2.metric("已录入成绩数", len(st.session_state.scores_df))
    
    if not st.session_state.scores_df.empty:
        pass_rate = round(len(st.session_state.scores_df[st.session_state.scores_df["总分"] >= 60]) / len(st.session_state.scores_df) * 100, 1)
        avg_score = round(st.session_state.scores_df["总分"].mean(), 1)
    else:
        pass_rate = 0
        avg_score = 0
    col3.metric("整体达标率", f"{pass_rate}%")
    col4.metric("平均总分", avg_score)

    st.subheader("使用说明")
    st.write("1. 先在「学生信息管理」中维护学生基础信息（含年级、性别）")
    st.write("2. 在「体质成绩录入」中录入体测成绩，系统自动计算得分与等级")
    st.write("3. 在「成绩查询与导出」中筛选数据、导出Excel报表")
    st.write("4. 在「学生历史成绩对比」中查看学生多学期成绩变化趋势")

# ---------- 学生信息管理 ----------
elif menu == "学生信息管理":
    st.subheader("👥 学生信息管理")
    st.caption("可直接在表格中编辑、新增、删除学生信息，年级必须填写（初一/初二/初三），用于自动评分")

    edited_df = st.data_editor(
        st.session_state.students_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="student_editor"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("保存修改", type="primary", use_container_width=True, key="save_student"):
            st.session_state.students_df = edited_df
            save_students(edited_df)
            st.success("学生信息已保存")

    st.divider()
    st.subheader("批量操作")
    if st.button("导出学生名单Excel", use_container_width=True, key="export_stu"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            st.session_state.students_df.to_excel(writer, index=False, sheet_name="学生名单")
        st.download_button(
            label="下载Excel文件",
            data=output.getvalue(),
            file_name="学生名单.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ---------- 体质成绩录入 ----------
elif menu == "体质成绩录入":
    st.subheader("📝 体质成绩录入")
    st.caption("录入成绩后系统自动对照国家标准计算单项得分、总分与等级")

    if st.session_state.students_df.empty:
        st.warning("请先在「学生信息管理」中添加学生基础信息")
    else:
        col1, col2 = st.columns(2)
        with col1:
            selected_class = st.selectbox("选择班级", sorted(st.session_state.students_df["班级"].unique()), key="score_class")
            class_students = st.session_state.students_df[st.session_state.students_df["班级"] == selected_class]
            selected_student = st.selectbox("选择学生", class_students["姓名"].tolist(), key="score_student")
            semester = st.selectbox("测试学期", ["2026-秋季", "2027-春季"], key="score_semester")

        student_info = class_students[class_students["姓名"] == selected_student].iloc[0]
        gender = student_info["性别"]
        grade = student_info["年级"]

        with col2:
            st.text(f"学号：{student_info['学号']}")
            st.text(f"性别：{gender}")
            st.text(f"年级：{grade}")

        st.divider()
        st.markdown("#### 基础信息")
        col_a, col_b = st.columns(2)
        height = col_a.number_input("身高(cm)", min_value=0.0, step=0.1, key="h")
        weight = col_b.number_input("体重(kg)", min_value=0.0, step=0.1, key="w")

        st.markdown("#### 体测项目")
        col_c, col_d, col_e = st.columns(3)
        vital = col_c.number_input("肺活量(ml)", min_value=0, step=1, key="v")
        run50 = col_d.number_input("50米跑(s)", min_value=0.0, step=0.1, key="r50")
        sit_reach = col_e.number_input("坐位体前屈(cm)", step=0.1, key="sr")

        col_f, col_g = st.columns(2)
        jump = col_f.number_input("立定跳远(cm)", min_value=0, step=1, key="lj")

        # 力量项目：按性别区分
        if gender == "男":
            strength = col_g.number_input("引体向上(次)", min_value=0, step=1, key="str")
            strength_label = "引体向上"
        else:
            strength = col_g.number_input("一分钟仰卧起坐(次)", min_value=0, step=1, key="str")
            strength_label = "一分钟仰卧起坐"

        # 耐力跑：按性别区分，分+秒输入
        st.markdown("#### 耐力跑")
        col_h, col_i, col_j = st.columns(3)
        run_min = col_h.number_input("分钟", min_value=0, step=1, key="run_min")
        run_sec = col_i.number_input("秒", min_value=0, max_value=59, step=1, key="run_sec")
        run_total = time_to_seconds(run_min, run_sec)
        col_j.metric("总秒数", run_total)

        if st.button("提交并自动评分", type="primary", key="submit_score"):
            # 计算各项目得分
            if gender == "男":
                vital_score = calc_score(MALE_VITAL, vital, grade, higher_better=True)
                run50_score = calc_score(MALE_RUN50, run50, grade, higher_better=False)
                sr_score = calc_score(MALE_SIT_REACH, sit_reach, grade, higher_better=True)
                jump_score = calc_score(MALE_JUMP, jump, grade, higher_better=True)
                str_score = calc_score(MALE_PULLUP, strength, grade, higher_better=True)
                run_score = calc_score(MALE_RUN1000, run_total, grade, higher_better=False)
            else:
                vital_score = calc_score(FEMALE_VITAL, vital, grade, higher_better=True)
                run50_score = calc_score(FEMALE_RUN50, run50, grade, higher_better=False)
                sr_score = calc_score(FEMALE_SIT_REACH, sit_reach, grade, higher_better=True)
                jump_score = calc_score(FEMALE_JUMP, jump, grade, higher_better=True)
                str_score = calc_score(FEMALE_SITUP, strength, grade, higher_better=True)
                run_score = calc_score(FEMALE_RUN800, run_total, grade, higher_better=False)

            # 计算总分（6项平均分，可按需调整权重）
            total_score = round((vital_score + run50_score + sr_score + jump_score + str_score + run_score) / 6, 1)
            level = get_level(total_score)

            new_record = pd.DataFrame([{
                "学号": student_info["学号"],
                "姓名": selected_student,
                "性别": gender,
                "年级": grade,
                "班级": selected_class,
                "测试学期": semester,
                "身高(cm)": height,
                "体重(kg)": weight,
                "肺活量(ml)": vital,
                "肺活量得分": vital_score,
                "50米跑(s)": run50,
                "50米跑得分": run50_score,
                "坐位体前屈(cm)": sit_reach,
                "坐位体前屈得分": sr_score,
                "立定跳远(cm)": jump,
                "立定跳远得分": jump_score,
                "力量项目成绩": strength,
                "力量项目得分": str_score,
                "耐力跑(秒)": run_total,
                "耐力跑得分": run_score,
                "总分": total_score,
                "等级": level
            }])

            st.session_state.scores_df = pd.concat([st.session_state.scores_df, new_record], ignore_index=True)
            save_scores(st.session_state.scores_df)
            st.success(f"录入成功！总分 {total_score} 分，等级：{level}")

# ---------- 成绩查询与导出 ----------
elif menu == "成绩查询与导出":
    st.subheader("📊 成绩查询与导出")

    if st.session_state.scores_df.empty:
        st.warning("暂无成绩数据")
    else:
        col1, col2, col3, col4 = st.columns(4)
        filter_class = col1.multiselect("筛选班级", sorted(st.session_state.scores_df["班级"].unique()), key="filter_c")
        filter_grade = col2.selectbox("筛选年级", ["全部"] + sorted(st.session_state.scores_df["年级"].unique().tolist()), key="filter_g")
        filter_semester = col3.selectbox("筛选学期", ["全部"] + sorted(st.session_state.scores_df["测试学期"].unique().tolist()), key="filter_s")
        filter_name = col4.text_input("搜索学生姓名", key="filter_n")

        result_df = st.session_state.scores_df.copy()
        if filter_class:
            result_df = result_df[result_df["班级"].isin(filter_class)]
        if filter_grade != "全部":
            result_df = result_df[result_df["年级"] == filter_grade]
        if filter_semester != "全部":
            result_df = result_df[result_df["测试学期"] == filter_semester]
        if filter_name:
            result_df = result_df[result_df["姓名"].str.contains(filter_name)]

        st.dataframe(result_df, use_container_width=True, hide_index=True)

        st.divider()
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("总记录数", len(result_df))
        if not result_df.empty:
            avg_total = round(result_df["总分"].mean(), 1)
            pass_rate = round(len(result_df[result_df["总分"] >= 60]) / len(result_df) * 100, 1)
            excellent_rate = round(len(result_df[result_df["等级"] == "优秀"]) / len(result_df) * 100, 1)
        else:
            avg_total = 0
            pass_rate = 0
            excellent_rate = 0
        col_b.metric("平均总分", avg_total)
        col_c.metric("达标率", f"{pass_rate}%")
        col_d.metric("优秀率", f"{excellent_rate}%")

        st.divider()
        if st.button("导出查询结果为Excel", type="primary", key="export_result"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                result_df.to_excel(writer, index=False, sheet_name="成绩数据")
            st.download_button(
                label="下载Excel文件",
                data=output.getvalue(),
                file_name="学生体测成绩数据.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# ---------- 学生历史成绩对比 ----------
elif menu == "学生历史成绩对比":
    st.subheader("📈 学生历史成绩对比")

    if st.session_state.scores_df.empty:
        st.warning("暂无多学期成绩数据，无法对比")
    else:
        select_student = st.selectbox(
            "选择学生",
            sorted(st.session_state.scores_df["姓名"].unique()),
            key="compare_stu"
        )
        student_history = st.session_state.scores_df[
            st.session_state.scores_df["姓名"] == select_student
        ].sort_values("测试学期")

        if student_history.empty:
            st.info("该学生暂无成绩记录")
        else:
            st.markdown(f"#### {select_student} 各学期成绩对比")
            # 总分与等级对比
            summary = student_history[["测试学期", "总分", "等级"]].set_index("测试学期")
            st.dataframe(summary, use_container_width=True)

            st.divider()
            st.markdown("#### 总分趋势图")
            st.line_chart(student_history.set_index("测试学期")["总分"])

            st.divider()
            st.markdown("#### 单项成绩对比")
            item = st.selectbox(
                "选择对比项目",
                ["肺活量得分", "50米跑得分", "坐位体前屈得分", "立定跳远得分", "力量项目得分", "耐力跑得分"],
                key="chart_item"
            )
            st.line_chart(student_history.set_index("测试学期")[item])
