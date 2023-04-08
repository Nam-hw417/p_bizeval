import pandas as pd
import numpy as np
import streamlit as st
from scipy import stats
from dateutil.relativedelta import relativedelta
from PIL import Image
from scipy.stats import wilcoxon

st.set_page_config(layout ='wide')
# <데이터 불러오기>


data = pd.read_csv('biz_data.csv', low_memory = False, dtype ={'사업시작월':str, '참가기업사업자번호':str})
exp_df = pd.read_csv('expamt_data.csv', low_memory = False, dtype ={'BSNO':str})
rec_df = pd.read_csv('biz_rec_30.csv', dtype ={'사업시작월':str, '참가기업사업자번호':str})


# <필요함수 작성>

# 1. 기준달이 주어지면 앞뒤 기간을 자동으로 계산하는 함수 

def make_basis_months(mon, basis = 12):
    mon_base = pd.to_datetime(mon+'01')
    mon_delta = relativedelta(months = basis)
   
    # 사업참가전 시작 년, 월 반환
    pre_str_mon = mon_base - mon_delta  
    pre_str_year =  str(pre_str_mon.year)
    pre_str_month  = pre_str_mon.month
    if len(str(pre_str_month)) == 1:
        pre_str_month = '0' + str(pre_str_month)
    else:
        pre_str_month = str(pre_str_month)
    pre_str_mon =  pre_str_year + pre_str_month
    
    # 사업참가전 종료 년, 월 반환
    pre_end_mon = mon_base - relativedelta(months=1)
    pre_end_year = str(pre_end_mon.year)
    pre_end_month =  pre_end_mon.month
    if len(str(pre_end_month)) ==1:
        pre_end_month = '0' + str(pre_end_month)
    else:
        pre_end_month = str(pre_end_month)    
    pre_end_mon = pre_end_year + pre_end_month
    
     # 사업참가후 시작 년, 월 반환
    post_str_mon = mon_base + relativedelta(months=1)  
    post_str_year =  str(post_str_mon.year)
    post_str_month =  post_str_mon.month
    if len(str(post_str_month)) ==1:
        post_str_month = '0' + str(post_str_month)
    else:
        post_str_month = str(post_str_month)
    post_str_mon =  post_str_year + post_str_month
    
    # 사업참가후 시작 년, 월 반환
    post_end_mon = mon_base + mon_delta  
    post_end_year =  str(post_end_mon.year)
    post_end_month =  post_end_mon.month
    if len(str(post_end_month)) ==1:
        post_end_month = '0' + str(post_end_month)
    else:
        post_end_month = str(post_end_month)
    post_end_mon =  post_end_year + post_end_month
    
    
    return pre_str_mon, pre_end_mon, post_str_mon, post_end_mon
    
# 2. 사업실적 평가 함수    
    
def eval_kotra_biz_re(biz_name, basis_month, period):
    
    try:
        pre_str_mon, pre_end_mon, post_str_mon, post_end_mon = make_basis_months(basis_month, period)
        idx = data[(data['사업명'] == biz_name) & (data['사업시작월'] == basis_month)]['참가기업사업자번호'].unique().tolist()
        if idx is None:
            st.write('입력값이 유효하지 않습니다.')
            pass
        result_df = exp_df[exp_df['BSNO'].isin(idx)]
        result_df.set_index('BSNO', inplace = True)
        pre = result_df.loc[:,  pre_str_mon:pre_end_mon].mean(axis =1)
        post = result_df.loc[:, post_str_mon:post_end_mon].mean(axis =1)
        dist = post - pre
        diff = post.mean() - pre.mean()
        w, p_value = wilcoxon(dist, alternative = 'greater')
        num_company = len(result_df)
        
        return num_company, pre_str_mon, pre_end_mon, pre.mean(), post_str_mon, post_end_mon, post.mean(), diff, p_value
    except:
        st.write('입력값이 유효하지 않습니다.')
        return
    
    

# 3. 샘플데이터 보여주는 함수

def show_biz_sample(biz_name):
    df = rec_df[rec_df['사업명'].str.contains(biz_name)]
    df = df[df['사업시작월'].str.contains('2019|2020|2021')]
    df = df[['사업명', '사업시작월']].set_index('사업시작월').sort_index(ascending = False)
    if len(df) > 15:
        df = df.head(15)
    return df 

# <화면구성>

# 1. 제목 및 부제



st.title('KOTRA Performance Measurement')

st.subheader('<성과측정원리: Wilcoxon 부호순위 검정>')

image = Image.open('wilcoxon.PNG')
st.image(image, caption='측정되지 않는 것은 관리되지 않는다 - 피터드러커')



# st.write('귀무가설(H0): 사업전후 월평균 수출액차이가 없음')
# st.write('대립가설(H1): 사업후 월평균 수출액이 사업전보다 크다')
# st.write('p-value 가 0.05미만일 경우 귀무가설기각, 대립가설 채택')

# st.header('2. 성과측정방법')
# st.write('1) CRM 사업명을 입력하고 사업시작월 입력')
# st.write('2) 사업효과가 날 것으로 예상되는 기간 입력: ex) 6, 9, 12 등')

# 2. 입력받을 값 결정


st.subheader('<사업성과측정>')

if 'biz_cat' not in st.session_state:
    st.session_state.biz_cat = '소비재'
    
    
# st.write('사업카테고리를 입력하세요 : ex) 지사화 / 전시회 / 신규수출기업화 etc.')
st.text_input(label = '사업명을 검색하세요', 
              max_chars = 15,
              key = 'biz_cat')

df = show_biz_sample(st.session_state.biz_cat)

st.text('사업명 검색결과 (사업일 기준 15개 사업)')
st.table(df)
st.write('')
st.write('')


col1, col2, col3 = st.columns([2.5, 0.9, 0.9])


if 'biz_name' not in st.session_state:
    st.session_state.biz_name ='소비재 수출초보기업 온라인 패키지 지원사업'

with col1:
    st.text_input(label = '사업명을 입력하세요', 
              max_chars = 55,
              key = 'biz_name')

if 'biz_month' not in st.session_state:
    st.session_state.biz_month ='202103'

with col2:
    st.text_input(label = '사업시작년월', 
              max_chars = 6,
              key = 'biz_month')

if 'period' not in st.session_state:
    st.session_state.period ='12'    

with col3:
    st.text_input(label = '사업전후 비교기간', 
              max_chars = 2,
              key = 'period')

num_company, pre_str_mon, pre_end_mon, pre_mean, post_str_mon, post_end_mon, post_mean, diff, p_value = eval_kotra_biz_re(st.session_state.biz_name, 
                  st.session_state.biz_month, int(st.session_state.period))


st.write('')
st.write('')
st.subheader('<성과측정결과>')
st.write('')

st.write('사업명: ', st.session_state.biz_name, '  / 사업시작월: ', st.session_state.biz_month)
st.write('사업참가 기업수: ', num_company, ' 개사')
# st.write('')
st.write('사업참가 전 비교기간: ', pre_str_mon, ' ~ ', pre_end_mon, ' / 월평균 수출금액 평균: $', format(int(pre_mean),','))
# st.write('사업참가 전 ', st.session_state.period, '개월 기업별 월평균수출금액평균: $', np.round(pre_mean))
#st.write('')
st.write('사업참가 후 비교기간: ', post_str_mon, ' ~ ', post_end_mon, ' / 월평균 수출금액 평균: $', format(int(post_mean),','))
# st.write('사업참가 후 ', st.session_state.period, '개월 기업별 월평균수출금액평균: $', np.round(post_mean))
st.write('사업참가 전후 월평균수출금액차이: $', format(int(diff), ','))
st.write('')
st.write('해당사업 Wilcoxon 순위합 검정의 p_value: ', np.round(p_value, 4))

if p_value < 0.05:
    if diff > 0:
        st.write('해당사업은 통계적으로 유효성이 입증됩니다.')
        st.write('해당사업의 ', st.session_state.period, '개월간 총효과는 $', 
             format(int(diff) * int(st.session_state.period) * num_company, ","), ' 로 추정됩니다.')
        st.caption('(총효과 추정식: 사업참가 기업수 x 사업전후 비교기간 x 월평균수출금액차이)')
    else:
        st.write('해당사업은 통계적으로 유효성이 입증되지 않습니다.')
else:
    st.write('해당사업은 통계적으로 유효성이 입증되지 않습니다.')
    

st.write('')
st.caption('E.O.P / Nam H.W.')


