import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import numpy as np

st.set_page_config(page_title="لوحة معلومات الموارد البشرية", layout="wide")

# CSS Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        background-color: #f5f8fc;
    }
    .metric-box {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
    }
    .section-header {
        font-size: 20px;
        color: #1e3d59;
        margin-top: 20px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

col_logo, col_upload = st.columns([1, 3])

with col_logo:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=180)
    except:
        st.warning("الشعار غير متوفر!")

with col_upload:
    st.markdown("<div class='section-header'>يرجى تحميل بيانات الموظفين</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("ارفع الملف", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None, header=0)
    selected_sheet = st.selectbox("اختر الجهة", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.duplicated()]

    # فلترة استبعاد الجهات وعمال البلدية
    excluded_departments = ['HC.نادي عجمان للفروسية', 'PD.الشرطة المحلية لإمارة عجمان', 'RC.الديوان الأميري']
    if 'الدائرة' in df.columns:
        df = df[~df['الدائرة'].isin(excluded_departments)]

    if 'الدائرة' in df.columns and 'الوظيفة' in df.columns:
        df = df[~((df['الدائرة'] == 'AM.دائرة البلدية والتخطيط') & (df['الوظيفة'] == 'عامل'))]

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        " نظرة عامة", 
        " تحليلات بصرية", 
        " البيانات المفقودة", 
        " عرض البيانات", 
        "تحليل الوظائف حسب الدوائر", 
        "تحليل العقود حسب الدوائر"
    ])

    with tab2:
        st.markdown("### التحليلات البصرية")

        if 'الجنسية' in df.columns:
            nationality_counts = df['الجنسية'].value_counts().reset_index()
            nationality_counts.columns = ['الجنسية', 'العدد']
            total_employees = nationality_counts['العدد'].sum()
            nationality_counts['النسبة المئوية'] = nationality_counts['العدد'] / total_employees * 100
            nationality_counts['النسبة المئوية'] = nationality_counts['النسبة المئوية'].round(1)

            st.write(f"**إجمالي عدد الجنسيات:** {nationality_counts.shape[0]}")

            fig_nat = px.bar(
                nationality_counts,
                x='الجنسية',
                y='العدد',
                text=nationality_counts['النسبة المئوية'].apply(lambda x: f"{x}%"),
                color='الجنسية',
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig_nat.update_layout(title='عدد الموظفين ونسبهم حسب الجنسية', title_x=0.5)
            st.plotly_chart(fig_nat, use_container_width=True)

    with tab3:
        st.markdown("### تحليل مفقودات عمود محدد")

        selected_column = st.selectbox("اختر عمود", df.columns)

        if selected_column:
            total = df.shape[0]
            missing = df[selected_column].isnull().sum()
            present = total - missing

            values = [present, missing]
            labels = ['موجودة', 'مفقودة']

            fig_donut = px.pie(
                names=labels,
                values=values,
                hole=0.5,
                color=labels,
                color_discrete_map={'مفقودة': '#C8D9E6', 'موجودة': '#2F4156'}
            )
            fig_donut.update_traces(
                text=[f'{v} | {round(v/total*100)}%' for v in values],
                textinfo='text+label'
            )
            fig_donut.update_layout(title=f"نسبة البيانات في العمود: {selected_column}", title_x=0.5)
            st.plotly_chart(fig_donut, use_container_width=True)

    with tab4:
        st.markdown("### عرض البيانات")
        st.dataframe(df)

    with tab5:
        st.markdown("### تحليل أنواع الوظائف حسب الدوائر")

        if 'الدائرة' in df.columns and 'الوظيفة' in df.columns:
            job_by_dept = df.groupby(['الدائرة', 'الوظيفة']).size().reset_index(name='العدد')
            pivot_table = job_by_dept.pivot(index='الدائرة', columns='الوظيفة', values='العدد').fillna(0)
            st.dataframe(pivot_table)

            fig_jobs = px.bar(
                job_by_dept,
                x='الدائرة',
                y='العدد',
                color='الوظيفة',
                barmode='group',
                title='عدد الموظفين حسب الوظيفة لكل دائرة'
            )
            fig_jobs.update_layout(xaxis_title='الدائرة', yaxis_title='عدد الموظفين', title_x=0.5)
            st.plotly_chart(fig_jobs, use_container_width=True)

    with tab6:
        st.markdown("### تحليل أنواع العقود حسب الدوائر")

        if 'الدائرة' in df.columns and 'نوع العقد' in df.columns:
            contract_by_dept = df.groupby(['الدائرة', 'نوع العقد']).size().reset_index(name='العدد')
            total_per_dept = contract_by_dept.groupby('الدائرة')['العدد'].transform('sum')
            contract_by_dept['النسبة المئوية'] = (contract_by_dept['العدد'] / total_per_dept * 100).round(1)
            st.dataframe(contract_by_dept)

            fig_contract = px.bar(
                contract_by_dept,
                x='الدائرة',
                y='العدد',
                color='نوع العقد',
                text=contract_by_dept['النسبة المئوية'].apply(lambda x: f"{x}%"),
                title='توزيع أنواع العقود لكل دائرة (Stacked)',
                barmode='stack'
            )
            fig_contract.update_layout(xaxis_title='الدائرة', yaxis_title='عدد الموظفين', title_x=0.5)
            st.plotly_chart(fig_contract, use_container_width=True)
