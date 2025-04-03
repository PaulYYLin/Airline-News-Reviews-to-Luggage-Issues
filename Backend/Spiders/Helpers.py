
import time
import requests
import numpy as np

from bs4 import BeautifulSoup
import dateutil.parser as dtparser



class Helpers:
    def __init__(self):
        pass
    #*************** Begin Skytrax Code ***************

    # this function returns number of pages for given a skytrax url
    def get_number_of_pages_skytrax(self, url):
        page = requests.get(url).text
        doc = BeautifulSoup(page, "html.parser")
        result = doc.find(class_="pagination__pagecount")
        if result is not None:
            return int(result.find_all("span")[-1].text)

    # this function extracts airline names for a given skytrax url
    def get_airline_names(self, url):
        page_count=self.get_number_of_pages_skytrax(url=url)
        airline_names=[]
        for p in range(1,page_count+1):
            print("Skytrax page "+ str(p)+ " is processing.")
            url_gen = url.split('?')[0]+'/page/'+str(p)+'?'+url.split('?')[1]
            page = requests.get(url_gen).text
            doc = BeautifulSoup(page, "html.parser")
            results = doc.find_all('div', class_="griditem-1-3 griditem-md-1-2 griditem-sm-1-1")
            temp = [str(r.find('a', href=True)['href']).split("/airlines/")[1] for r in results]

            for t in temp:
                if t.split('-')[-2] != 'safety':
                    airline_names.append('-'.join(t.split('-')[:-1]))
                else:
                    if t.split('-')[-3] == 'airline':
                        airline_names.append('-'.join(t.split('-')[:-5]))

                    elif  t.split('-')[-3] == '19':
                        airline_names.append('-'.join(t.split('-')[:-4]))
                if airline_names[-1].split('-')[-1]=='star':
                    airline_names[-1]= '-'.join(airline_names[-1].split('-')[:-2])
        return np.unique(airline_names)

    #*************** End Skytrax Code ***************

    #*************** Begin Airline Quality Code ***************

            
    # this function returns number of pages for a given an airline quality url
    def get_number_of_pages_airline_quality(self,airline_name):
        url = "https://www.airlinequality.com/airline-reviews/" + airline_name
        page_number = "/page/1/"
        page = requests.get(url + page_number).text
        doc = BeautifulSoup(page, "html.parser")
        r = doc.find(class_="comp comp_reviews-pagination querylist-pagination position-")
        if r is not None:
            return int(str(r.find_all("a", href=True)[-2]['href']).split("/")[-2])
        else:
            return 1

    # this function parse a airline quality page to a dictionary
    # ub_date : upper bound for review date
    # lb_date: lowr bound for review date
    def review_parser(self,reviews, ub_date, lb_date):

        # create  dictionary initialized with None elements as the number of reviews
        rev_dict = {'review_date': [None for i in range(len(reviews))], 'over_all_rating': [None for i in range(len(reviews))], 'review_header': [None for i in range(len(reviews))],
                    'trip_verified': [None for i in range(len(reviews))], 'review_text': [None for i in range(len(reviews))], 'aircraft': [None for i in range(len(reviews))],
                    'type_of_traveller': [None for i in range(len(reviews))], 'seat_type': [None for i in range(len(reviews))], 'route': [None for i in range(len(reviews))],
                    'date_flown': [None for i in range(len(reviews))], 'seat_comfort': [None for i in range(len(reviews))], 'cabin_staff_service': [None for i in range(len(reviews))],
                    'food__beverages': [None for i in range(len(reviews))], 'inflight_entertainment': [None for i in range(len(reviews))], 'ground_service': [None for i in range(len(reviews))],
                    'wifi__connectivity': [None for i in range(len(reviews))], 'value_for_money': [None for i in range(len(reviews))], 'recommended': [None for i in range(len(reviews))]}
        # addd review values to dictionary
        for c, rev in enumerate (reviews):
            # get review date
            review_date = rev.find('meta',{'itemprop':  "datePublished"})['content'] if rev.find('meta', {'itemprop': 'datePublished'}) is not None else None
            # here the code assumes that, the reviews are fetched in descended order and, stops parsing if the review date is lower than the date_limit

            if review_date is not None:
                review_date=dtparser.parse(review_date)
                if review_date>=lb_date:
                    if review_date<=ub_date:
                        rev_dict['review_date'][c]=review_date
                        rev_dict['over_all_rating'][c]= rev.find('span',{'itemprop': 'ratingValue'}).text.strip() if rev.find('span',{'itemprop': 'ratingValue'}) is not None else None
                        rev_dict['review_header'][c]=rev.find('h2',class_='text_header').text.strip() if rev.find('h2',class_='text_header') is not None else None
                        review_body = rev.find("div", {"itemprop": "reviewBody"}, class_="text_content")

                        if review_body is not None:
                            rev_dict['trip_verified'][c]= review_body.find("strong").text if review_body.find("strong") is not None else None
                            rev_dict['review_text'][c]='.'.join(review_body.text.strip().split('.')[1:])

                        review_ratings = rev.find("table", class_="review-ratings")
                        if review_ratings is not None:
                            rating_classes_and_values = [[i.text, len(i.find_all("span", class_ = "star fill" ))] for i in  review_ratings.find_all("td", class_=True)]
                            for i in range(0,len(rating_classes_and_values),2):
                                if  rating_classes_and_values[i+1][0].strip().lower().replace('&', '').replace(' ','_') == '12345':

                                    rev_dict[rating_classes_and_values[i][0].strip().lower().replace('&', '').replace(' ','_')][c]= rating_classes_and_values[i+1][1]
                                else:
                                    rev_dict[rating_classes_and_values[i][0].strip().lower().replace('&', '').replace(' ', '_')][c]=rating_classes_and_values[i + 1][0].strip().lower().replace('&', '').replace(' ', '_')
                    else:
                        continue
                else:
                    print(str(review_date)+ " is too old.")
                    return False

        return rev_dict

    # this function gets reviews for a given airline name

    def get_reviews(self,airline_name,ub_date, lb_date):
        total_pages = 1
        print(str(total_pages)+ " pages are found for "+ airline_name+".")
        for page in range(1, total_pages + 1):
            print("Page " + str(page) + " is processing.")
            url = f"https://www.airlinequality.com/airline-reviews/" + airline_name + f"/page/{page}/"
            doc = BeautifulSoup(requests.get(url).text, "html.parser")
            s_time=10
            while doc.find_all(class_="col-content") is  None or  len( doc.find_all(class_="col-content"))<3:
                time.sleep(s_time)
                s_time += 10
                print(doc)
                print( doc.find_all(class_="col-content"))
                doc = BeautifulSoup(requests.get(url).text, "html.parser")

            reviews = doc.find_all(class_="col-content")[2].find_all("article", {"itemprop": "review"})

            reviews_parsed = self.review_parser(reviews=reviews, ub_date=ub_date, lb_date=lb_date)
            if reviews_parsed == False:
                break
            else:
                return reviews_parsed