# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# -*- coding: utf-8 -*-
# import necessary packages

import dataiku
import pandas as pd, numpy as np
import logging
import time
import os
import schedule
import time
import smtplib, ssl

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

from dataiku import pandasutils as pdu
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from imap_tools import MailBox, AND, A

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# define the variable

client = dataiku.api_client()
project = client.get_project("SARC_RD_WEARHOUSE_REPORTS_7v8q5FRU")
handle = dataiku.Folder("row_wearhouse_reports")
path_war = handle.get_path()

handleOld = dataiku.Folder("wearhouse_row_compning_ok_month")
pathOld = handleOld.get_path()

handleDis = dataiku.Folder("dis_row_data")
path_dis = handleDis.get_path()
resultsWerar = "NOT TEST IT YET!"

df = "NOT SET YET!"
tt = "NOT SET YET!"
tt2 = "NOT SET YET!"
disdf = "NOT SET YET!"
distt = "NOT SET YET!"
distt2 = "NOT SET YET!"

color = 'not set yet'

#is_pass_open_balance = 1
isPassStatus = 1
isPassDis = 1

total_sum_of_closing_sum_for_old = 0
total_sum_of_open_balnce_for_now = 0
email = "rd.sarc.im.ca@gmail.com"
emailPassword = "fijrbnvyolqscuro"

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# get list of email from INBOX folder for your rd.sarc email and it's to the right folder
#TO DO
#-hide email password as variable in dataiku..
def geting_email():
    status = 0
    with MailBox('imap.gmail.com').login(email, emailPassword) as mailbox:
        if mailbox.fetch(A(seen=False)):
            for msg in mailbox.fetch(A(seen=False)):
                replyFor= msg.from_
                subject = msg.subject
                if msg.attachments:
                    for att in msg.attachments:
                        if "old-hq" in att.filename.lower():
                            with open('{}/{}'.format(pathOld, att.filename.replace(att.filename, "old_data.xlsx")), 'wb') as old:
                                old.write(bytearray(att.payload))
                                status = 5
                            return status, replyFor, subject
                        elif "old" in att.filename.lower():
                            pass
                        elif "war" in att.filename.lower():
                            with open('{}/{}'.format(path_war, att.filename.replace(att.filename, "warehouse15.xlsx")), 'wb') as war:
                                war.write(bytearray(att.payload))
                                status = 1
                        elif  "dis" in att.filename.lower() :
                            with open('{}/{}'.format(path_dis, att.filename.replace(att.filename, "dis.xlsx")), 'wb') as dis:
                                dis.write(bytearray(att.payload))
                                status = 1
                            return status, replyFor, subject
                        else:
                            status = 2
                            return status, replyFor, subject
                else:
                    status = 3
                    return status, replyFor, subject

  #  no_new_message = 3
   # return no_new_message
    status = 4
    replyFor = None
    subject = None

    return status, replyFor, subject

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def old_check_build():
    project.get_dataset("Rural_Damascus___Warehouse__September_2020__2_").clear(partitions=None)
    project.get_dataset("Rural_Damascus___Warehouse__September_2020__2_").build()
    project.get_dataset("wearhouse_row_compning_ok_month_prepared").build()
    project.get_dataset("test_tarek_month").build()

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def war_check_build():
    project.get_dataset("wearhouse_row_data").clear(partitions=None)
    project.get_dataset("wearhouse_row_data").build()
    project.get_dataset("wearhouse_row_data_prepared").build()
    project.get_dataset("wearhouse_row_data_prepared_grouping").build()
    project.get_dataset("wearhous_row_and_month_joined_to_check_openbalne").build()
    project.get_dataset("final_check").build()

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def dis_check_build():
    project.get_dataset("dis_row_dataset").clear(partitions=None)
    project.get_dataset("dis_row_dataset").build()
    project.get_dataset("dis_row_dataset_prepared").build()
    project.get_dataset("dis_row_dataset_prepared_by_SubBranch").build()
    project.get_dataset("wearhouse_row_data_prepared_prepared_for_dis").build()
    project.get_dataset("wearhouse_row_data_for_check_wiht_dis").build()
    project.get_dataset("dis_row_dataset_prepared_by_SubBranch_joined").build()
    project.get_dataset("final_check_dis").build()

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def color_style(val):
    color = 'white'
    if (val == 'false') or (val == 0):
        color = 'red'
    elif val == 'ok':
        color = 'grey'

    return 'border-width:2px; background-color :%s' % color
# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def old_war_check():
    #geting the need df datafram
    war_to_check = dataiku.Dataset("final_check")
    old_war_df = war_to_check.get_dataframe()

    war_to_check_total_out = dataiku.Dataset("wearhouse_row_data_for_check_wiht_dis")
    war_total_out = war_to_check_total_out.get_dataframe()

    war_to_check_empty_value = dataiku.Dataset("wearhouse_row_data_prepared")
    empty_war_df = war_to_check_empty_value.get_dataframe()

    #set the variables
    counts_of_check_status_open_balnce = old_war_df['check_status_open_balnce'].value_counts()
    counts_of_check_status = old_war_df['check_status'].value_counts()
    total_sum_of_closing_sum_for_old = old_war_df['old_Closing_Balance_sum'].sum()
    total_sum_of_open_balnce_for_now = old_war_df['Open_Balance_sum'].sum()
    total_sum_of_out_to_check_from_war = war_total_out['Total_out_sum'].sum()
    #check that all the items total from previous month is there
    if (total_sum_of_closing_sum_for_old == total_sum_of_open_balnce_for_now):
        is_pass_previosu_month = False
    else:
        is_pass_previosu_month = True

    #you need this for that is there no "ok" in any coulm will consding all the data as
    #bollen and when there is ok all the data type will be string
    if "ok" in counts_of_check_status_open_balnce:
        is_pass_open_balance = 'false' in counts_of_check_status_open_balnce
    else:
        is_pass_open_balance = 0 in counts_of_check_status_open_balnce

    #check for your empty value
    is_pass_war_empty_value = "EMPTY" in empty_war_df[{'Branch_Code','Sub_Branch_code'}].values

    #write the results in excel after styling, sorting
    old_war_df.sort_values(by=['check_status_open_balnce','check_status'],ascending=True).style.applymap(color_style, subset=['check_status_open_balnce','check_status']).to_excel(r'%s/results.xlsx' % (path_war), index = False)
    results_war_excel = '%s/results.xlsx' % (path_war)

    return counts_of_check_status_open_balnce, counts_of_check_status, total_sum_of_closing_sum_for_old, total_sum_of_open_balnce_for_now,is_pass_previosu_month, is_pass_open_balance, is_pass_war_empty_value, total_sum_of_out_to_check_from_war, results_war_excel

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def dis_check():
    #geting the need df datafram
    dis_to_check = dataiku.Dataset("final_check_dis")
    dis_df = dis_to_check.get_dataframe()

    dis_to_check_empty_value = dataiku.Dataset("dis_row_dataset_prepared")
    empty_dis_df = dis_to_check_empty_value.get_dataframe()

    #set the total out and check total in
    total_sum_of_out_to_check_from_dis = dis_df['Quantity_sum'].sum()

    #set the variables
    counts_of_check_status_dis = dis_df['check_dis_and_total_out'].value_counts()

    #check dis and waerhouse at true and flase
    is_Pass_Dis = 0 in counts_of_check_status_dis

    #check for your empty value
    is_pass_dis_empty_value = "EMPTY" in empty_dis_df[{'District','SubDistrict','Community','Location','Dis_type','Total Number of Beneficiaries','Beneficiary Condition','Beneficiary condition main','GovCode','DistrictCode','SubDistrictCode','Community Pcode'}].values
    #write the results in excel after styling, sorting
    dis_df.sort_values(by='check_dis_and_total_out',ascending=True).style.applymap(color_style, subset='check_dis_and_total_out').to_excel(r'%s/results.xlsx' % (path_dis), index = False)
    results_dis_excel = '%s/results.xlsx' % (path_dis)

    return counts_of_check_status_dis, is_Pass_Dis, is_pass_dis_empty_value, total_sum_of_out_to_check_from_dis,results_dis_excel

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def bulid_final_dataset_war_dis():
    project.get_dataset("wearhouse_row_data_prepared_check_ok").build()
    project.get_dataset("dis_row_dataset_prepared_to_ready_to_collect").build()

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def sedning_email(replyFor, subject,results,counts_of_check_status_open_balnce, counts_of_check_status,
                  total_sum_of_closing_sum_for_old, total_sum_of_open_balnce_for_now,
                  is_pass_previosu_month, is_pass_open_balance,
                  is_pass_war_empty_value, total_sum_of_out_to_check_from_war, counts_of_check_status_dis,
                  is_Pass_Dis, is_pass_dis_empty_value,
                  total_sum_of_out_to_check_from_dis, results_war_excel, results_dis_excel,is_Pass_Dis_with_war_as_total):
    msg = MIMEMultipart()
    # setup the parameters of the message
    password = emailPassword
    msg['From'] = "rd.sarc.im.ca@gmail.com"
    #just for testing 
    #msg['to'] = "rd.sarc.im.ca@gmail.com"
    msg['To'] = str(replyFor)
    msg['Subject'] = "SARC IM AUTO SYSTEM %s" % (subject)
    body = MIMEText("""<style>.email-style{direction: rtl;}</style>
                    <div class="email-style">
                    <h2>نتائج الأختبار الأخير: """ + str(results) + """ </h2>

                    <h3>حركة المستودع:</h3>
                    <table>
                        <tr>
                            <td>مجموع الرصيد الشهر الحالي مع الشهر الماضي:</td>
                            <td>""" + str(total_sum_of_closing_sum_for_old)  + """ / """ + str(total_sum_of_open_balnce_for_now) + """</td>
                        </tr>
                        <tr>
                            <td> مطابقة الرصيد الأفتتاحي مع الشهر الماضي: </td>
                            <td>""" + str(not is_pass_previosu_month) + """</td>
                        </tr>
                        <tr>
                            <td> التفاصيل :</td>
                            <td>""" + str(counts_of_check_status_open_balnce) + """</td>
                        </tr>
                        <tr>
                            <td>الرصيد الختامي للشهر نفسه: </td>
                            <td>""" + str(is_pass_open_balance) + """</td>
                        </tr>
                        <tr>
                            <td> التفاصيل: </td>
                            <td>""" + str(counts_of_check_status) + """</td>
                        </tr>
                        <tr>
                            <td>وجود خلايا فارغة في حركة المستودع:</td>
                            <td>""" + str(is_pass_war_empty_value) + """</td>
                        </tr>
                    </table>

                    <h3>إستمارة التوزيع</h3>
                    <table>
                        <tr>
                            <td>مجموع الرصيد المواد الصادرة مع المواد الموزعة:</td>
                            <td>""" + str(total_sum_of_out_to_check_from_dis) + """ / """ + str(total_sum_of_out_to_check_from_war) + """ </td>
                        </tr>
                        <tr>
                            <td>مطابقة الكمية مع المواد الصادرة على مستوى المجموع:</td>
                            <td>""" + str(is_Pass_Dis_with_war_as_total) + """</td>
                        </tr>
                        <tr>
                            <td>مطابقة الكمية مع المواد الصادرة على مستوى المادة:</td>
                            <td>""" + str(not is_Pass_Dis) + """</td>
                        </tr>
                        <tr>
                            <td> التفاصيل :</td>
                            <td>""" + str(counts_of_check_status_dis) + """</td>
                        </tr>
                        <tr>
                            <td>وجود خلايا فارغة في استمارة التوزيع:</td>
                            <td>""" + str(is_pass_dis_empty_value) + """</td>
                        </tr>
                    </table>


                    <h4>الخلايا التالية يجب أن لا تكون فارغة في حركة المستودع، حيث يقوم البرنامج بفحص العواميد التالية: </h4>
                    <ul>
                        <li>Branch Code</li>
                        <li>Sub Branch code</li>
                    </ul>

                    <h4>الخلايا التالية يجب أن لا تكون فارغة في استمارة التوزيع، حيث يقوم البرنامج بفحص العواميد التالية: </h4>
                    <ul>
                        <li>District</li>
                        <li>SubDistrict</li>
                        <li>Community</li>
                        <li>Location</li>
                        <li>Total Number of Beneficiaries</li>
                        <li>Beneficiary Condition</li>
                        <li>Beneficiary condition main</li>
                        <li>GovCode</li>
                        <li>DistrictCode</li>
                        <li>SubDistrictCode</li>
                        <li>Community Pcode</li>
                        <li>Dis_type</li>
                    </ul>
                    </div>""", 'html', 'utf-8')

    msg.attach(body)
    # attach image to message body
    fp = open(results_war_excel, 'rb')
    part = MIMEBase('application','vnd.ms-excel')
    part.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename='results_w.xlsx')

    fp2 = open(results_dis_excel, 'rb')
    part2 = MIMEBase('application','vnd.ms-excel')
    part2.set_payload(fp2.read())
    fp2.close()
    encoders.encode_base64(part2)
    part2.add_header('Content-Disposition', 'attachment', filename='results_d.xlsx')

    msg.attach(part)
    msg.attach(part2)

    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)


    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def sedning_email_wrong(replyFor, subject):
    msg = MIMEMultipart()
    # setup the parameters of the message
    password = emailPassword
    msg['From'] = email
    msg['To'] = str(replyFor)
    msg['Subject'] = "SARC IM AUTO SYSTEM %s" % (subject)
    body = MIMEText("""<style>.email-style{direction: rtl;}</style>
                    <div class="email-style">
                    <h4>هنالك خطأ ما في الملفات المرفقة، يرجى مراجعة دليل الإستخدام المرسل سابقاً.</h4>

                    </div>""", 'html', 'utf-8')

    msg.attach(body)

    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)


    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def sedning_email_for_admin(replyFor, subject):
    msg = MIMEMultipart()
    # setup the parameters of the message
    password = emailPassword
    msg['From'] = email
    msg['To'] = str(replyFor)
    msg['Subject'] = "SARC IM AUTO SYSTEM %s" % (subject)
    body = MIMEText("""<style>.email-style{direction: rtl;}</style>
                    <div class="email-style">
                    <h4>تم تسجيل ملف OLD ضمن البرنامج بنجاح.</h4>
                    </br>
                    <h4>يرجى ملاحظة انه لا يتم تدقيق او معالجة أي شي ضمن الملف المضاف، لذلك يرجى التأكد منه جيداً قبل رفعه. .</h4>

                    </div>""", 'html', 'utf-8')

    msg.attach(body)

    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)


    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def controller ():
    status, replyFor,subject = geting_email()
    if (status == 4):
        #nothing to do
        pass
    elif (status == 5):
        old_check_build()
        sedning_email_for_admin(replyFor, subject)
    elif (status == 2) or (status == 3):
        sedning_email_wrong(replyFor, subject)
    elif status == 1:
        war_check_build()
        dis_check_build()
        old_war_check()
        dis_check()
        counts_of_check_status_open_balnce, counts_of_check_status,total_sum_of_closing_sum_for_old, total_sum_of_open_balnce_for_now,is_pass_previosu_month, not(is_pass_open_balance),is_pass_war_empty_value, total_sum_of_out_to_check_from_war, results_war_excel = old_war_check()
        counts_of_check_status_dis, is_Pass_Dis, is_pass_dis_empty_value, total_sum_of_out_to_check_from_dis, results_dis_excel = dis_check()

        if (total_sum_of_closing_sum_for_old == total_sum_of_open_balnce_for_now) and (total_sum_of_out_to_check_from_war == total_sum_of_out_to_check_from_dis) and (not is_pass_previosu_month) and (not is_pass_open_balance) and (not is_pass_war_empty_value) and (not is_Pass_Dis) and (not is_pass_dis_empty_value ):
            results = "نجاح التحقق"
            is_Pass_Dis_with_war_as_total = (total_sum_of_out_to_check_from_war == total_sum_of_out_to_check_from_dis)
            bulid_final_dataset_war_dis()
        else:
            results = "فشل التحقق"
            is_Pass_Dis_with_war_as_total = (total_sum_of_out_to_check_from_war == total_sum_of_out_to_check_from_dis)

        sedning_email(replyFor, subject,results,counts_of_check_status_open_balnce, counts_of_check_status,total_sum_of_closing_sum_for_old, total_sum_of_open_balnce_for_now,is_pass_previosu_month, is_pass_open_balance,is_pass_war_empty_value, total_sum_of_out_to_check_from_war,counts_of_check_status_dis, is_Pass_Dis, is_pass_dis_empty_value, total_sum_of_out_to_check_from_dis, results_war_excel, results_dis_excel,is_Pass_Dis_with_war_as_total)
        controller()

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
schedule.every(1).minutes.do(controller)

while True:
    schedule.run_pending()
    time.sleep(1)