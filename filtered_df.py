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

    # استبعاد جهات معينة
    excluded_departments = ['HC.نادي عجمان للفروسية', 'PD.الشرطة المحلية لإمارة عجمان', 'RC.الديوان الأميري']
    if 'الدائرة' in df.columns:
        df = df[~df['الدائرة'].isin(excluded_departments)]

    tab1, tab2, tab3, tab4 = st.tabs([" نظرة عامة", " تحليلات بصرية", " البيانات المفقودة", " عرض البيانات"])

    with tab2:
        st.markdown("### التحليلات البصرية")

        # فلترة استبعاد عاملين البلدية
        if 'الدائرة' in df.columns and 'الوظيفة' in df.columns:
            analysis_df = df[~((df['الدائرة'] == 'AM.دائرة البلدية والتخطيط') & (df['الوظيفة'] == 'عامل'))].copy()
        else:
            analysis_df = df.copy()

        if 'الجنسية' in analysis_df.columns:
            nationality_counts = analysis_df['الجنسية'].value_counts().reset_index()
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
            fig_nat.update_layout(title='عدد الموظفين ونسبهم حسب الجنسية', title_x=0.5, xaxis_title='الجنسية', yaxis_title='عدد الموظفين')
            st.plotly_chart(fig_nat, use_container_width=True)

            st.markdown("#### جدول الجنسيات مع العدد والنسبة:")
            st.dataframe(nationality_counts)

            # Pie Chart
            fig_pie = px.pie(
                nationality_counts,
                names='الجنسية',
                values='العدد',
                hole=0.3,
                title='نسبة الموظفين حسب الجنسية (Pie Chart)',
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

            # Box per 5 rows
            st.markdown("### تفاصيل الجنسيات (كل 5 في صف):")
            colors = px.colors.sample_colorscale("Blues", [i/len(nationality_counts) for i in range(len(nationality_counts))])

            for i in range(0, len(nationality_counts), 5):
                row = nationality_counts.iloc[i:i+5]
                cols = st.columns([1]*len(row))
                for idx, (j, data) in enumerate(row.iterrows()):
                    with cols[idx]:
                        st.markdown(f"""
                            <div style='
                                background-color:{colors[idx]};
                                padding: 10px;
                                border-radius: 10px;
                                text-align: center;
                                color: white;
                                font-size: 14px;
                                font-weight: bold;
                                height: 100px;
                                display: flex;
                                flex-direction: column;
                                justify-content: center;'>
                                {data['الجنسية']}<br>
                                {data['العدد']} موظف ({data['النسبة المئوية']}%)
                            </div>
                        """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

    with tab3:
        st.markdown("###  تحليل مفقودات عمود محدد")

        # فلترة استبعاد عاملين البلدية
        if 'الدائرة' in df.columns and 'الوظيفة' in df.columns:
            filtered_df = df[~((df['الدائرة'] == 'AM.دائرة البلدية والتخطيط') & (df['الوظيفة'] == 'عامل'))].copy()
        else:
            filtered_df = df.copy()

        selected_column = st.selectbox("اختر عمود", filtered_df.columns)

        if selected_column:
            total = filtered_df.shape[0]
            missing = filtered_df[selected_column].isnull().sum()
            present = total - missing

            values = [present, missing]
            labels = ['موجودة', 'مفقودة']

            fig_donut = px.pie(
                names=labels,
                values=values,
                hole=0.5,
                color=labels,
                color_discrete_map={
                    'مفقودة': '#C8D9E6',
                    'موجودة': '#2F4156'
                }
            )
            fig_donut.update_traces(
                text=[f'{v} | {round(v/total*100)}%' for v in values],
                textinfo='text+label'
            )
            fig_donut.update_layout(title=f"نسبة البيانات في العمود: {selected_column}", title_x=0.5)
            st.plotly_chart(fig_donut, use_container_width=True)


        else:
            st.warning("يرجى رفع ملف بيانات الموظفين أولًا.")
