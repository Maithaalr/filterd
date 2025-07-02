import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

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

# Custom Colors
custom_colors = ['#4B6A8A', '#577D91', '#2F3E51', '#A1BCC8', '#6E8F9D', '#2E424D']

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

    # ---- فلترة عامة ----
    excluded_departments = ['HC.نادي عجمان للفروسية', 'PD.الشرطة المحلية لإمارة عجمان', 'RC.الديوان الأميري']
    if 'الدائرة' in df.columns:
        df = df[~df['الدائرة'].isin(excluded_departments)]

    if 'الدائرة' in df.columns and 'الوظيفة' in df.columns:
        df = df[~((df['الدائرة'] == 'AM.دائرة البلدية والتخطيط') & (df['الوظيفة'] == 'عامل'))]

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        " نظرة عامة", 
        " تحليلات بصرية", 
        " البيانات المفقودة", 
        " عرض البيانات", 
        "تحليل الوظائف حسب الدوائر", 
        "تحليل العقود حسب الدوائر",
        "تحليل نسبة الوظائف"
    ])

    # --------- Tab 2 ---------
    with tab2:
        st.markdown("### التحليلات البصرية")

        filtered_df = df.copy()

        # تحليل الجنسيات
        if 'الجنسية' in filtered_df.columns:
            nationality_counts = filtered_df['الجنسية'].value_counts().reset_index()
            nationality_counts.columns = ['الجنسية', 'العدد']
            total = nationality_counts['العدد'].sum()
            nationality_counts['النسبة المئوية'] = (nationality_counts['العدد'] / total * 100).round(1)

            fig_nat = px.bar(
                nationality_counts,
                x='الجنسية',
                y='العدد',
                text=nationality_counts['النسبة المئوية'].apply(lambda x: f"{x}%"),
                color='الجنسية',
                color_discrete_sequence=custom_colors
            )
            fig_nat.update_layout(title='عدد الموظفين حسب الجنسية', title_x=0.5)
            st.plotly_chart(fig_nat, use_container_width=True)

            fig_pie = px.pie(
                nationality_counts,
                names='الجنسية',
                values='العدد',
                hole=0.3,
                color_discrete_sequence=custom_colors
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        # ✅ تحليل الجنس
        if 'الجنس' in filtered_df.columns:
            gender_counts = filtered_df['الجنس'].value_counts().reset_index()
            gender_counts.columns = ['الجنس', 'العدد']

            fig_gender = px.bar(
                gender_counts,
                x='الجنس',
                y='العدد',
                color='الجنس',
                text='العدد',
                color_discrete_sequence=custom_colors
            )
            fig_gender.update_layout(title='عدد الموظفين حسب الجنس', title_x=0.5)
            st.plotly_chart(fig_gender, use_container_width=True)

    # --------- Tab 3 ---------
    with tab3:
        st.markdown("### تحليل البيانات المفقودة")
        selected_column = st.selectbox("اختر العمود لتحليل المفقودات", df.columns)
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
                color_discrete_map={'موجودة': custom_colors[0], 'مفقودة': custom_colors[3]}
            )
            fig_donut.update_layout(title=f"مفقودات العمود: {selected_column}", title_x=0.5)
            st.plotly_chart(fig_donut, use_container_width=True)

    # --------- Tab 4 ---------
    with tab4:
        st.markdown("### عرض البيانات")
        st.dataframe(df)

    # --------- Tab 5 ---------
    with tab5:
        st.markdown("### تحليل أنواع الوظائف حسب الدوائر")
        if 'الدائرة' in df.columns and 'الوظيفة' in df.columns:
            job_by_dept = df.groupby(['الدائرة', 'الوظيفة']).size().reset_index(name='العدد')
            fig_jobs = px.bar(
                job_by_dept,
                x='الدائرة',
                y='العدد',
                color='الوظيفة',
                barmode='group',
                color_discrete_sequence=custom_colors,
                title='عدد الموظفين حسب الوظيفة لكل دائرة'
            )
            fig_jobs.update_layout(xaxis_title='الدائرة', yaxis_title='عدد الموظفين', title_x=0.5)
            st.plotly_chart(fig_jobs, use_container_width=True)
            st.dataframe(job_by_dept)

    # --------- Tab 6 ---------
    with tab6:
        st.markdown("### تحليل أنواع العقود حسب الدوائر")
        if 'الدائرة' in df.columns and 'نوع العقد' in df.columns:
            contract_by_dept = df.groupby(['الدائرة', 'نوع العقد']).size().reset_index(name='العدد')
            total_per_dept = contract_by_dept.groupby('الدائرة')['العدد'].transform('sum')
            contract_by_dept['النسبة المئوية'] = (contract_by_dept['العدد'] / total_per_dept * 100).round(1)

            fig_contract = px.bar(
                contract_by_dept,
                x='الدائرة',
                y='العدد',
                color='نوع العقد',
                text=contract_by_dept['النسبة المئوية'].apply(lambda x: f"{x}%"),
                color_discrete_sequence=custom_colors,
                barmode='stack',
                title='توزيع أنواع العقود لكل دائرة'
            )
            fig_contract.update_layout(xaxis_title='الدائرة', yaxis_title='عدد الموظفين', title_x=0.5)
            st.plotly_chart(fig_contract, use_container_width=True)
            st.dataframe(contract_by_dept)

    # --------- Tab 7 ---------
    with tab7:
        st.markdown("### نسبة كل نوع وظيفة داخل كل جهة")

        if 'الدائرة' in df.columns and 'الوظيفة' in df.columns:
            job_counts = df.groupby(['الدائرة', 'الوظيفة']).size().reset_index(name='العدد')
            total_per_dept = job_counts.groupby('الدائرة')['العدد'].transform('sum')
            job_counts['النسبة المئوية'] = (job_counts['العدد'] / total_per_dept * 100).round(1)

            fig_job_ratio = px.bar(
                job_counts,
                x='الدائرة',
                y='العدد',
                color='الوظيفة',
                text=job_counts['النسبة المئوية'].apply(lambda x: f"{x}%"),
                color_discrete_sequence=custom_colors,
                barmode='stack',
                title='توزيع الوظائف داخل كل جهة (Stacked %)'
            )
            fig_job_ratio.update_layout(xaxis_title='الدائرة', yaxis_title='عدد الموظفين', title_x=0.5)
            st.plotly_chart(fig_job_ratio, use_container_width=True)
            st.dataframe(job_counts)
