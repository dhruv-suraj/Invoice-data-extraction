import pytesseract
import shutil
import numpy as np
import cv2
import re
import os
import pandas as pd
from PIL import Image
import csv
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import torch
import string
from craft_text_detector import (
    read_image,
    load_craftnet_model,
    load_refinenet_model,
    get_prediction,
    export_detected_regions,
    export_extra_results,
    empty_cuda_cache
)

# set image path and export folder directory
image_dir = 'C:/Users/Shreyansh/Desktop/invoices/images_type'
output_dir = 'C:/Users/Shreyansh/Desktop/invoices'
image_crops_dir='C:/Users/Shreyansh/Desktop/invoices/image_crops'
with open('extracted_DL.csv', 'w', encoding='UTF8',newline='') as f:
        writess = csv.writer(f)
        header = ['BUYER NAME','SELLER NAME','GSTIN','FSSAI NO','INVOICE DATE','PRODUCT NAME']
        writess.writerow(header)
        for filename in os.listdir(image_dir):
        # check if file is an image
            if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
                 # read image
                # image_path = os.path.join(image_dir, filename)
                image_path='C:/Users/Shreyansh/Desktop/invoices/images/4 gandhi traders_page-0001.jpg'

                img = cv2.imread(image_path)

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # overwrite the original image with grayscale image
                cv2.imwrite(image_path, gray)

                image = read_image(image_path)


                # load models
                refine_net = load_refinenet_model(cuda=False)
                craft_net = load_craftnet_model(cuda=False)

                # perform prediction
                prediction_result = get_prediction(
                    image=image,
                    craft_net=craft_net,
                    refine_net=refine_net,
                    text_threshold=0.7,
                    link_threshold=0.4,
                    low_text=0.4,
                    cuda=False,
                    long_size=1280
                )

                # export detected text regions
                exported_file_paths = export_detected_regions(
                    image=image,
                    regions=prediction_result["boxes"],
                    output_dir=output_dir,
                    rectify=True
                )


                export_extra_results(
                    image=image,
                    regions=prediction_result["boxes"],
                    heatmaps=prediction_result["heatmaps"],
                    output_dir=output_dir
                )
                

                texts=[]
                for filename in os.listdir(image_crops_dir):
                    # print(image)
                # check if file is an image
                    if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
                        # print(filename,"FILENAME")
                        image_crop_path = os.path.join(image_crops_dir, filename)
                        img = Image.open(image_crop_path)
                        max_width = 1400
                        max_height = 1200
                        # Get the current dimensions of the image
                        width, height = img.size
                        # Determine the new dimensions while maintaining the aspect ratio
                        aspect_ratio = width / float(height)
                        if aspect_ratio > 1:
                            new_width = max_width
                            new_height = int(max_width / aspect_ratio)
                        else:
                            new_height = max_height
                            new_width = int(max_height * aspect_ratio)
                        # Resize the image with the new dimensions
                        img = img.resize((new_width, new_height), resample=Image.BICUBIC)
                        # Save the image with the new resolution
                        img.save('output_image.png')
                        text = pytesseract.image_to_string('C:/Users/Shreyansh/output_image.png',config='--psm 6')
                        texts.append(text)
                new_list = []
                for item in texts:
                    item = item.replace('\n', '').replace('\x0c', '').replace('|','').replace('{','').replace('}','').replace('(','').replace(')','')
                    new_list.append(item)
                print(new_list,image_path)

                gst_id = None
                fssai = None
                unique_gst = []
                unique_fssai = []
                invoice_dates=[]
                final_amount=[]
                product_name=[]
                buyers=[]
                sellers=[]
                df_products = pd.read_excel("C:/Users/Shreyansh/Downloads/List products.xlsx")
                product_names = df_products["Product Name"].str.lower().tolist()
                df_partymaster=pd.read_excel("C:/Users/Shreyansh/Downloads/PARTY MASTER..xlsx")
                party_names = df_partymaster["Party Name"].str.upper().tolist()
                fssai_nos = df_partymaster["FSSAI"].tolist()
                for item in new_list:
                    #Extract PRODUCT NAME
                    for name in product_names:
                        # name=name.split(" ")
                        s=item.split(" ")
                        # print(name)
                        for i in s:
                            # for n in name:
                                if name == i.lower():
                                    product_name.append(item)
                    # EXTRACT GSTIN
                    gst_matches = re.findall(r"\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}", item)
                    if gst_matches:
                        gst_number = gst_matches[-1]
                        if gst_number not in unique_gst:
                            unique_gst.append(gst_number)
                    #EXTRACT FSSAI
                    fssai_matches = re.findall(r"[0-9]{14}", item)
                    if fssai_matches:
                        if "account" not in item.lower():
                            if "policy" not in item.lower():
                                fssai_number = fssai_matches[-1]
                                if fssai_number not in unique_fssai:
                                    unique_fssai.append(fssai_number)
                    elif 'FSSAI: ' in item and '/' in item:
                        fssai_number = item.replace('/', '')[7:]
                        if fssai_number not in unique_fssai:
                            unique_fssai.append(fssai_number)
                    #EXTRACT INVOICE DATE
                    regex = r'(date|dated)\s*[:.]?\s*\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b\d{4}[-/]\d{2}[-/]\d{2}\b|\b\d{1,2}\s(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2,4}\b|\b\d{1,2}[ ./-](?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[ ./-]\d{2,4}\b|\b\d{1,2}[ /-]\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b[ /-]\d{2,4}\b|\b\d{1,2}[/]\d{1,2}[/]\d{2,4}\b'
                    match = re.search(regex,item,re.IGNORECASE)
                    if match:
                        invoice_dates.append(match.group(0))
                        date_match = re.search(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b\d{4}[-/]\d{2}[-/]\d{2}\b|\b\d{1,2}\s(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2,4}\b|\b\d{1,2}[ ./-](?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[ ./-]\d{2,4}\b', match.group(0))
                        if date_match:
                            invoice_dates.append(date_match.group(0))
                #EXTRACT BUYER AND SELLER NAMES            
                if len(unique_fssai)==2:
                    try:
                        buyer = fssai_nos.index(int(unique_fssai[0]))
                    except ValueError:
                        buyer='NOT IN THE PARTY MASTER'
                    if buyer!='NOT IN THE PARTY MASTER':
                        buyers.append(party_names[buyer])
                        # print(party_names[buyer])
                    try:    
                        seller=fssai_nos.index(int(unique_fssai[1]))
                    except ValueError:
                        seller='NOT IN THE PARTY MASTER'
                    if seller!='NOT IN THE PARTY MASTER':
                        sellers.append(party_names[seller])
                        # print(party_names[seller])
                elif len(unique_fssai)==1:
                    try:
                        buyer = fssai_nos.index(int(unique_fssai[0]))
                    except ValueError:
                        buyer='NOT IN THE PARTY MASTER'
                    if buyer!='NOT IN THE PARTY MASTER':
                        buyers.append(party_names[buyer])

                
                    # decimals = re.findall(r"\d+\.\d+", item)
                    # if decimals:
                    #     decimals=''.join(decimals)
                    #     final_amount.append(decimals)
                        # print(decimals,type(decimals))
                # weight = 0
                # rate = 0
                # amount = 0
                # print(final_amount)
                # final_amount_float = [float(x) for x in final_amount]
                # for i in range(len(final_amount)):
                #     for j in range(i+1, len(final_amount)):
                #         result = (float(final_amount[i]) * float(final_amount[j]))/float(100) or (float(final_amount[i]) * float(final_amount[j]))
                #         if result in final_amount_float:
                #             weight = min(float(final_amount[i]), float(final_amount[j]))
                #             rate = max(float(final_amount[i]), float(final_amount[j]))
                #             print("WEIGHT",weight,"RATE",rate,"AMOUNT",result)


                for product in product_name:
                    data=[''.join(buyers[-1]) if buyers else '',''.join(sellers[-1]) if sellers else '',' '.join(unique_gst),'  '.join(unique_fssai),invoice_dates[-1] if invoice_dates else '',product]
                    print(data) 
                    writess.writerow(data)    
                    

                

                break
                shutil.rmtree(image_crops_dir)
                # create new output directory
                os.makedirs(image_crops_dir)
                # unload models from gpu
                empty_cuda_cache()
                


