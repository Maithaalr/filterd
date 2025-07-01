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
        st.markdown("### تحليل البيانات المفقودة")

        # فلترة استبعاد عاملين البلدية
        if 'الدائرة' in df.columns and 'الوظيفة' in df.columns:
            filtered_df_missing = df[~((df['الدائرة'] == 'AM.دائرة البلدية والتخطيط') & (df['الوظيفة'] == 'عامل'))].copy()
        else:
            filtered_df_missing = df.copy()

        # حساب عدد ونسبة المفقودات
        missing_count = filtered_df_missing.isnull().sum()
        missing_percent = filtered_df_missing.isnull().mean() * 100

        missing_summary = pd.DataFrame({
            'العمود': missing_count.index,
            'عدد القيم المفقودة': missing_count.values,
            'النسبة المئوية': missing_percent.values.round(2)
        })

        # فقط الأعمدة اللي فيها مفقودات
        missing_summary = missing_summary[missing_summary['عدد القيم المفقودة'] > 0]

        if not missing_summary.empty:
            st.markdown("#### إجمالي القيم المفقودة (باستثناء عاملين البلدية):")
            st.dataframe(missing_summary)

            fig_missing = px.bar(
                missing_summary,
                x='العمود',
                y='عدد القيم المفقودة',
                color='النسبة المئوية',
                text=missing_summary.apply(lambda row: f"{row['عدد القيم المفقودة']} | {row['النسبة المئوية']}%", axis=1),
                color_continuous_scale=['#C8D9E6', '#2F4156']
            )
            fig_missing.update_layout(title="إجمالي القيم المفقودة", title_x=0.5, xaxis_tickangle=-45)
            st.plotly_chart(fig_missing, use_container_width=True)
        else:
            st.success("لا توجد قيم مفقودة بعد استبعاد عاملين البلدية 🎉")

else:
    st.warning("يرجى رفع ملف بيانات الموظفين أولًا.")
