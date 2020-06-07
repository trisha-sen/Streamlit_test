# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 14:01:31 2020

@author: tsen6
"""

import streamlit as st
st.title("My Streamlit App")

clicked = st.button("Click Me")

if clicked:
    st.balloons()
    
