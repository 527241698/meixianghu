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
