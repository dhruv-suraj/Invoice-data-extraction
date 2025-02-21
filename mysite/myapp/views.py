from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
import pytesseract as pytesseract
import re
from PIL import Image
from .forms import FileUpload
from .models import *
from django.urls import reverse
import os
from django.conf import settings
import csv
from io import BytesIO
from io import TextIOWrapper
from io import StringIO
from django.core.files.storage import FileSystemStorage
import tabula
import pandas as pd
import re
from pdfminer.high_level import extract_text
from io import BytesIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
# Create your views here.
def home(request):
    users = User.objects.all()
    if users.count()>0:
        return render(request, 'home.html',{'users':users})
    else:
        return render(request, 'home.html')

def uploadpdf(request):
        if request.method=="POST":
            # print("shhh")
            # form = FileUpload(request.POST, request.FILES)
            pdf_files = request.FILES.getlist('imageupload')
                    # Save the PDF files to the media folder
            fs = FileSystemStorage()
            filenames = []
            for pdf_file in pdf_files:
                filename = fs.save('uploads/' + pdf_file.name, pdf_file)
                filenames.append(filename)
            print(filenames)
            # Generate the CSV file based on the uploaded PDF files
            # writer.writerow(['Title', 'Number of Pages'])


            substring='none'
            date=''
            with open('extracted.csv', 'w', encoding='UTF8',newline='') as f:
                writess = csv.writer(f)
                header = ['FILENAME','SELLER NAME','BUYER NAME','GSTIN','FSSAI','INVOICE DATE','SR NO','ITEM NAME','HSN CODE','WEIGHT','RATE','AMOUNT','FINAL AMOUNT']
                writess.writerow(header)
                for pdf_file in pdf_files:
                            print(pdf_file)
                            with fs.open('uploads/' + pdf_file.name) as f:
                                # try:
                                    df = tabula.read_pdf(pdf_file, multiple_tables=True, pandas_options={'header': None},pages="all")
                                    tabula.convert_into(pdf_file,r"xyz.csv", output_format="csv", pages="all")
                                    csv_file="xyz.csv"
                                    if pdf_file.content_type == 'application/pdf':
                                        resource_manager = PDFResourceManager()
                                        output_stream = BytesIO()
                                        converter = TextConverter(resource_manager, output_stream, laparams=LAParams())
                                        page_interpreter = PDFPageInterpreter(resource_manager, converter)

                                        for page in PDFPage.get_pages(pdf_file.file):
                                            page_interpreter.process_page(page)

                                        text = output_stream.getvalue().decode()
                                        converter.close()
                                        output_stream.close()
                                    # print(text)
                                    with open('xyz.csv', newline='') as csvfile:
                                            reader = csv.reader(csvfile)

                                            # read all rows and concatenate them into a single string
                                            rows_str = ''.join([','.join(row) for row in reader])

                                            # print the concatenated string
                                            # print(rows_str)
                                    if os.stat(csv_file).st_size == 0:
                                        print("NOT A COMPUTER GENERATED INVOICE ")
                                        data = [pdf_file,'','','']
                                        print(data)

                                        # write the data
                                        writess.writerow(data)
                                    else:
                                        # print(text,type(text))
                                        new_list=[]
                                        unique_gst=[]
                                        unique_fssai=[]

                                        df_products = pd.read_excel("C:/Users/Shreyansh/Downloads/List products.xlsx")
                                        product_names = df_products["Product Name"].str.lower().tolist()
                                        df_partymaster=pd.read_excel("C:/Users/Shreyansh/Downloads/PARTY MASTER..xlsx")
                                        party_names = df_partymaster["Party Name"].str.upper().tolist()
                                        fssai_nos = df_partymaster["FSSAI"].tolist()
                                        lists=list(text.split("\n"))
                                        # print(lists)
                                        for item in lists:
                                            item = item.replace('\n', '').replace('\x0c', '')
                                            new_list.append(item)
                                        # print(new_list)
                                        for t in new_list:
                                            gst_matches = re.findall(r"\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}", t)
                                            if gst_matches:
                                                gst_number = gst_matches[-1]
                                                if gst_number not in unique_gst:
                                                    unique_gst.append(gst_number)                                
                                            fssai_matches = re.findall(r"[0-9]{14}",t)
                                            if fssai_matches:
                                                if "account" not in item.lower():
                                                    if "policy" not in item.lower():
                                                        fssai_number = fssai_matches[-1]
                                                        print(fssai_number,"FSSAI")
                                                        if fssai_number not in unique_fssai and len(unique_fssai)<2:
                                                            unique_fssai.append(fssai_number)
                                        # print(text)
                                        match = re.search(r'\bdate\s*[:\-/.]?\s*(\d{1,2}[/:.-]\d{1,2}[/:.-]\d{2,4})\b', text, re.IGNORECASE)
                                        if match:
                                            date = match.group(1)
                                            print(date,"hii")
                                        else:
                                            # if date is None:
                                                match = re.search(r'\b(date|dated)\s*[:\-/.]?\s*(\d{1,2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2,4})\b', text, re.IGNORECASE) or re.search(r'\b(date|dated)\s*[:\-/.]?\s*(\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{2,4})\b',text,re.IGNORECASE)

                                                if match:
                                                    date = match.group(2)
                                                    print(date,"hello")
                                        y= re.findall("\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}",text)
                                        if y:
                                            unique_values = set(y)
                                            output_gst = list(unique_values)
                                            gst=''.join(output_gst[-1])
                                        else:
                                            gst=' '
                                            # print(output_gst[-1],"GST")

                                        x = re.findall("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]",text)
                                        if x and "FSSAI" in rows_str:
                                            unique_values = set(x)
                                            output_fssai = list(unique_values)
                                            fssai=''.join(output_fssai[-1])
                                            # print(output_fssai[-1],"FSSAI")
                                        else:
                                            fssai=' '
                                        with open("xyz.csv", 'r') as input_file:
                                            reader = csv.reader(input_file)
                                            res=[]
                                            total_amount=[]
                                            for row in reader:
                                                row=[s.replace('\n',' ')for s in row]
                                                lets=' '.join(row)

                                                # print(lets)
                                                # if "Bill No." in lets:
                                                #     print(lets)

                                                # print(type(lets))
                                                if re.match(r'^\d.*\w+.*[0-9]+(\.[0-9]+)?$',lets):
                                                    lets=lets.split()
                                                    # print(lets)
                                                    if(len(lets)>6):
                                                        lets=' '.join(lets)
                                                        res.append(lets)
                                                        # details='\n'.join(res)
                                                        # words=details.split()
                                                        # total_amount.append(words[-1])
                                                        # data = [filename,gst,fssai,details,date,words[-1]]
                                                        # # print(amount[-1],"AMOUNT")

                                                else:
                                                    for cell in row:
                                                        # print(type(cell))
                                                        if re.match(r'^\d.*\w+.*[0-9]+(\.[0-9]+)?$', cell):
                                                            cell=cell.split()
                                                            # print(cell)
                                                            # print(cell)
                                                            if(len(cell)>6):
                                                                result = ' '.join(cell)
                                                                res.append(result)
                                                                # print(cell,"PRODUCT DETAILS")
                                                                # details='\n'.join(res)
                                                                # words=details.split()
                                                                # total_amount.append(words[-1])



                                        #EXTRACT BUYER AND SELLER NAMES 
                                        buyers=[]
                                        sellers=[]           
                                        if len(unique_fssai)==2:
                                            try:
                                                seller = fssai_nos.index(int(unique_fssai[0]))
                                            except ValueError:
                                                seller='NOT IN THE PARTY MASTER'
                                            if seller!='NOT IN THE PARTY MASTER':
                                                sellers.append(party_names[seller])
                                                # print(party_names[buyer])
                                            try:    
                                                buyer=fssai_nos.index(int(unique_fssai[1]))
                                            except ValueError:
                                                buyer='NOT IN THE PARTY MASTER'
                                            if buyer!='NOT IN THE PARTY MASTER':
                                                buyers.append(party_names[buyer])
                                                # print(party_names[seller])
                                        elif len(unique_fssai)==1:
                                            try:
                                                seller = fssai_nos.index(int(unique_fssai[0]))
                                            except ValueError:
                                                seller='NOT IN THE PARTY MASTER'
                                            if seller!='NOT IN THE PARTY MASTER':
                                                sellers.append(party_names[seller])

                                        # sh=[]
                                        # amount=[]
                                        print(res,"hellllllll")
                                        my_list=[]
                                        for r in res:
                                            description=r
                                            words=r.split()
                                            print(words[0],"SR NO")
                                            hsn = re.findall("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]",description)
                                            print(hsn,"HSN")
                                            if hsn:
                                                # print(hsn,"HSN NO")
                                                hsn=''.join(hsn)
                                                if hsn!=words[0]:
                                                    start = description.index(words[0])
                                                    end = description.index(hsn,start+1)

                                                    substring = description[start+1:end]
                                            else:
                                                hsn='19041020'
                                                substring=description.split()
                                                substring=' '.join(substring[1:5])
                                                print(substring)
                                            my_list.append(substring)

                                            description=description.split()
                                            my_numbers = []

                                            description = [item for item in description if '(' not in item and ')' not in item and '%' not in item and '?' not in item]
                                            print(description)
                                            for item in description:
                                                # Remove commas from string
                                                item = item.replace(',', '')
                                                # Check if item is a float
                                                if '.' in item:
                                                    item = int(float(item))
                                                # Check if item is an integer
                                                elif item.isdigit():
                                                    item = int(item)
                                                if isinstance(item, int) and item > 10:
                                                    # Add to numbers list
                                                    my_numbers.append(item)
                                                # Add to numbers list
        

                                            print(my_numbers)
                                            other_number=0
                                            matching_number=0
                                            number=0
                                            seen_numbers = set()
                                            w_r_found=False
                                            for number in my_numbers:
                                                if number in seen_numbers:
                                                    continue
                                                for other_number in my_numbers:
                                                    if number != other_number and other_number != 0 and number % other_number == 0 and number // other_number in my_numbers:
                                                        matching_number = number // other_number
                                                        # print(other_number, matching_number, number)
                                                        w_r_found=True
                                                        break
                                                seen_numbers.add(number)
                                                if w_r_found:
                                                    break
                                            weight_rate_amount=[other_number,matching_number,number]
                                            weight_rate_amount=sorted(weight_rate_amount,reverse=True)
                                            # print("AMOUNT",weight_rate_amount[0])
                                            # print("RATE",weight_rate_amount[1])
                                            # print("WEIGHT",weight_rate_amount[2])

                                            # print(weight_rate_amount)
                                            data = [pdf_file,''.join(sellers[-1]) if sellers else '',''.join(buyers[-1]) if buyers else '','  '.join(unique_gst),'  '.join(unique_fssai),date,words[0],substring,hsn,weight_rate_amount[2],weight_rate_amount[1],weight_rate_amount[0],words[-1]] 
                                            print(data) 
                                            writess.writerow(data)
                                            user = User(file_name=pdf_file,seller_name=''.join(sellers[-1]) if sellers else 'NOT IN THE PARTY MASTER',buyer_name=''.join(buyers[-1]) if buyers else 'NOT IN THE PARTY MASTER',gst_no='  '.join(unique_gst),fssai_no='  '.join(unique_fssai),invoice_date=date,sr_no=words[0],item_name=substring,hsn_code=hsn,weight=weight_rate_amount[2],rate=weight_rate_amount[1],amount=weight_rate_amount[0],final_amount=words[-1],description=description)
                                            user.save()
                                            url = reverse('product_master', kwargs={'item_name': substring})

     
                                # except:
                                #     print("An error occurred while extracting data from the file.")

                    # pdf_bytes = f.read()
                    # number_of_pages = pdf_bytes.count(b'/Type /Page')
                    # writer.writerow([pdf_file.name, number_of_pages])
            # upload_completed = True

            # print(substring,"substring")
            # url = reverse('product_master', kwargs={'item_name': 'pulav'})
            # url = reverse('product_master', kwargs={'item_name': substring})
            return redirect(url)
            # return render(request,'home.html', {'upload_completed': upload_completed})
        else:
             return render(request,'home.html')

def downloadpdf(request):
        with open('extracted.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            # Create a response object with the CSV file contents
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="extracted.csv"'
            writer = csv.writer(response)

            # Loop through each row and write it to the response object
            for row in csv_reader:
                writer.writerow(row)
        return response

def download_all(request):
    user = User.objects.all()

    # Convert queryset to a pandas DataFrame
    df = pd.DataFrame(list(user.values()))

    # Create response object with content type 'application/vnd.ms-excel'
    response = HttpResponse(content_type='application/vnd.ms-excel')

    # Set the Content-Disposition header to force download the file
    response['Content-Disposition'] = 'attachment; filename=extracted_all.xlsx'

    # Write DataFrame to Excel file and attach to response object
    df.to_excel(response, index=False)

    return response

def product_master(request,item_name):
    print(item_name,"heyy")
    # Get the list of products and brands from the database
    products = Products.objects.values_list('product_name', flat=True)
    brands = Brand.objects.values_list('brand_name', flat=True)

    # Convert the queryset to a list and remove duplicates
    data_products = list(set(products))
    data_brand = list(set(brands))

    # Remove all spaces from the input name and all possible combinations
    input_name = item_name.replace(" ", "").lower()
    data_products = [str(x).replace(" ", "").lower() for x in data_products]
    data_brand = [str(x).replace(" ", "").lower() for x in data_brand]
    combinations = [product + brand for product in data_products for brand in data_brand] + \
                [brand + product for brand in data_brand for product in data_products]
    combinations = [cb.replace(" ", "").lower() for cb in combinations]

    # Create two empty dataframes for the output
    df_matched = pd.DataFrame(columns=['Input Name'])
    df_not_matched = pd.DataFrame(columns=['Input Name'])

    # Check if input_name is a product name
    if input_name in data_products:
        df_matched = df_matched.append({'Input Name': input_name}, ignore_index=True)
        print("INSIDE THE PRODUCT MASTER",input_name)

    else:
        # Remove everything after the first numeric character
        input_name = re.sub(r'\d.*', '', input_name)
        # Check if the input name matches any possible combination
        match_found = False
        for cb in combinations:
            if input_name == cb:
                match_found = True
                break
        if match_found:
            df_matched = df_matched.append({'Input Name': input_name}, ignore_index=True)
            messages.success(request,'PART OF THE PRODUCT MASTER.')
            print("INSIDE THE PRODUCT MASTER",input_name)
        else:
            df_not_matched = df_not_matched.append({'Input Name': input_name}, ignore_index=True)
            messages.error(request, 'NOT A PART OF THE PRODUCT MASTER.')
            print("NOT INSIDE THE PRODUCT MASTER",input_name)

    return redirect('home')