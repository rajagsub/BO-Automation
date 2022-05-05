import pandas as pd
import pdfplumber
from datetime import date
import time


# Extracting BPD File and appending to bpd_pdf_data_pages
def extract_bpd_file(bpd_file_path):
    global bpd_pdf_data_pages
    # Loading the pdf_data_pages list with the PDF data.
    with pdfplumber.open(bpd_file_path) as pdf:
        total_pages = len(pdf.pages)
        for i in range(0, total_pages):
            page = pdf.pages[i]
            text = page.extract_text()
            for t in text.split("\n"):
                bpd_pdf_data_pages.append(t)


# Extracting BO File and appending to bpd_pdf_data_pages
def extract_bo_file(bo_file_path):
    global bo_pdf_data_pages
    # Loading the bo_pdf_data_pages list with the PDF data.
    with pdfplumber.open(bo_file_path) as pdf:
        total_pages = len(pdf.pages)
        for i in range(0, total_pages):
            page = pdf.pages[i]
            text = page.extract_text()
            for l in text.split("\n"):
                bo_pdf_data_pages.append(l)


def get_val_bo_file():
    # Fetch Process for Bo file
    # Main logic to lopp thru the reference input file and check the BO PDF file LIST.
    bo_pdf_data_pages_len = len(bo_pdf_data_pages)
    percent = 'PCT '
    for input1 in bo_ref:
        # input1 = ' ' + input1 + ' ' --> Raj
        input1 = ' ' + input1
        for i in range(0, bo_pdf_data_pages_len):
            if (input1 in bo_pdf_data_pages[i]) and (percent in bo_pdf_data_pages[i]):
                percent_val = bo_pdf_data_pages[i].split(percent)[-1].strip()
                percent_val_final = percent_val[:3]
                bo_pct_val.append(percent_val_final)
                break
        else:
            bo_pct_val.append('0')


# Matching Process for BPD file
def get_val_bpd_file(bpd_ref, bpd_network):
    # Main logic to lopp thru the reference input file and check the PDF file LIST.
    bpd_pdf_data_pages_len = len(bpd_pdf_data_pages)
    limit = 'Limit :'
    covered = 'Covered'
    not_covered = 'Not Covered'
    covered_at = 'Covered At :'
    covered_at_1 = 'At the In Network'
    covered_at_2 = 'At the INN benefit'
    percentage = '%'
    for i in range(0, len(bpd_ref)):
        covered_val_final_in = ' '
        covered_val_final_out = ' '
        not_covered_flag = 'N'
        in_covered_flag = 'N'
        second_line = bpd_second_line[i]
        if second_line == '?':
            second_line = ''
        #        bpd_ref[i] = 'Hearing Aid Services'
        #        second_line = ''
        #        bpd_ref[i] = 'Exam - Routine Adult physical'
        #        second_line = ''
        #        bpd_ref[i] = 'Emergency – Emergency Room'
        #        second_line = 'Physician'
        #        bpd_ref[i] = 'Hearing exam (routine)'
        #        second_line = ''
        #        bpd_ref[i] = 'Non-Emergency Medical Condition –'
        #        second_line = 'Emergency Room (Institutional)'
        for j in range(0, bpd_pdf_data_pages_len):
            if (bpd_ref[i] in bpd_pdf_data_pages[j] and (covered in bpd_pdf_data_pages[j]) and (
                    second_line in bpd_pdf_data_pages[j] or second_line in bpd_pdf_data_pages[j + 1])):
                # print("hello", bpd_pdf_data_pages[j])
                # print("hi", bpd_pdf_data_pages[j + 1])
                if covered_at_1 in bpd_pdf_data_pages[j] or covered_at_2 in bpd_pdf_data_pages[j]:
                    in_covered_flag = 'Y'
                    # print("found1")
                if not_covered in bpd_pdf_data_pages[j] and bpd_pdf_data_pages[j].count(not_covered) > 1:
                    not_covered_flag = 'Y'
                    # print("found2")
                if not_covered in bpd_pdf_data_pages[j] and bpd_pdf_data_pages[j].count(covered) == 1:
                    not_covered_flag = 'Y'
                    # print("found3")
                j = j + 1
                while True:
                    if (covered_at in bpd_pdf_data_pages[j]) and (percentage in bpd_pdf_data_pages[j]):

                        if bpd_pdf_data_pages[j].count(percentage) >= 2:
                            covered_val_in = bpd_pdf_data_pages[j].split(':')[-2]
                            covered_val_final_in = covered_val_in.strip().split('%')[0]
                            covered_val_out = bpd_pdf_data_pages[j].split(':')[-1]
                            covered_val_final_out = covered_val_out.strip().split('%')[0]
                        else:
                            covered_val_in = bpd_pdf_data_pages[j].split(':')[-1]
                            covered_val_final_in = covered_val_in.strip().split('%')[0]
                            # print('covered_val_final_in:',covered_val_final_in)
                            covered_val_final_out = ' '
                            if in_covered_flag == 'Y':
                                covered_val_final_out = covered_val_final_in
                                in_covered_flag = 'N'
                        break
                    else:
                        j = j + 1
                    if limit in bpd_pdf_data_pages[j] or not_covered_flag == 'Y':
                        break
        if bpd_network[i] == 'in':
            bpd_pct_val.append(covered_val_final_in)
        else:
            bpd_pct_val.append(covered_val_final_out)
        if bo_pct_val[i].strip(' ') == bpd_pct_val[i].strip(' '):
            bo_bpd_compare.append('Matched')
        elif bo_pct_val[i] == '0' and bpd_pct_val[i] == ' ':
            bo_bpd_compare.append('Not Found in Both')
        else:
            bo_bpd_compare.append('Unmatched')


def write_df_to_csv(planname):
    # This is to write final percentage values from BO and BPD to excel sheet
    dict = {'BO Ref': bo_ref, 'BPD Ref': bpd_ref, 'BPD Network': bpd_network, 'BPD Second': bpd_second_line,
            'BO Pct': bo_pct_val, 'BPD Pct': bpd_pct_val, 'Output': bo_bpd_compare}
    dffinal = pd.DataFrame(dict)
    dffinal = dffinal.replace(to_replace="â€“", value="-", regex=True)
    dffinal.to_excel('Comparison Report ' + planname + '.xlsx', index=False)


if __name__ == '__main__':
    print("****************************FFS Comparison Started********************")
    current_day = date.today()
    start = time.time()
    print("Today's Date:", current_day)

    # Initializing BPD Values
    bpd_pdf_data_pages = []

    # Initializing BO Values
    bo_pdf_data_pages = []
    bo_counter = 0

    # Initializing Values
    bo_ref = []
    bpd_ref = []
    bpd_network = []
    bpd_second_line = []

    # Output List
    bo_pct_val = []
    bpd_pct_val = []
    bo_bpd_compare = []

    # Reading paths file where PDF file locations are stored
    path_file = r"C:\Users\af40411\PycharmProjects\BO_PDF_Extraction\Final_BO_vs_BPD_Automation\FFS Plan\FFS_Path.txt"
    file1 = open(path_file)
    lines = file1.readlines()
    for l in lines:
        value = l.split(',')
        for val in range(0, len(value)):
            if val == 0:
                epo_bpd_file_path = value[0]
                temp_planname = epo_bpd_file_path.split('.pdf')
                temp_planname1 = temp_planname[0].strip(" ")
                # planname = temp_planname[0][-5:-1]
                planname = temp_planname1[-4:]
            if val == 1:
                epo_bo_file_path = value[1]

    # Reading the mapping file for BO and BPD reference
    mapping_file = r"C:\Users\af40411\PycharmProjects\BO_PDF_Extraction\Final_BO_vs_BPD_Automation\FFS Plan\Mapping-Z3QR.txt"

    with open(mapping_file) as f:
        datas = f.readlines()

    for d in datas:
        value = d.split(',')
        # bo_ref.append()
        for val in range(0, len(value)):
            if val == 0:
                bo_ref.append(value[0])
            if val == 1:
                bpd_ref.append(value[1])
            if val == 2:
                bpd_network.append(value[2].strip())
            if val == 3:
                bpd_second_line.append(value[3].strip())

    # Extract the BPD PDF in text format
    extract_bpd_file(epo_bpd_file_path)

    # Extract the BO PDF in text format
    extract_bo_file(epo_bo_file_path)
    #    print(bo_pdf_data_pages)

    # Process Bo File and filter matching data from reference file { THis should be appended to bo_pct_val list}
    get_val_bo_file()

    # Process BPD file and filter the matching data from reference file
    get_val_bpd_file(bpd_ref, bpd_network)

    # Writing final percentage values from BO and BPD to excel sheet
    write_df_to_csv(planname)

    end = time.time()
    print(f"Runtime of the program is {end - start}")
    print("****************************FFS Comparison Ended********************")