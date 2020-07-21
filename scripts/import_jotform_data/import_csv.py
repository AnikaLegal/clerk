import csv, requests, json

q_ids = {
    "Anika Legal: Student Impact Survey (Pre-Case)" : [
        "q3_iHave",
        "q5_iFeel5",
        "q6_clientCommunication",
        "q7_draftingLegal7",
        "q8_iCan",
        "q9_iAm",
        "q10_iHave11",
        "q11_iAm11",
        "q12_iAm13",
        "q13_iAm13",
        "q20_iAm20",
        "q19_iAm19",
        "q21_iAm21",
        "q14_iDiscuss15",
        "q15_iDiscuss16",
        "q17_iAm18",
        "q22_iAm22",
        "q16_iPlan17",
        "q18_pastOpportunities18",
        "q23_pastOpportunities23"
    ],

    "Anika Legal COVID-19 Product Survey" : [
        "q4_q1How",
        "q6_q3",
        "q7_q3How",
        "q8_q5How",
        "q9_q5How9",
        "q10_q7Howclear",
        "q12_q7How",
        "q13_q8How",
        "q16_q9How16",
        "q14_q10Was",
        "q15_q11Was"
    ]
}


def send_data(data):
    url = "http://localhost:8000/api/webhooks/jotform-form/"
    res = requests.post(url, data=data)
    print(res.json())

def process_row(form_title, row):
    raw_request = {}
    # Fill raw_request
    if form_title == "Anika Legal: Student Impact Survey (Pre-Case)":
        raw_request["q2_fullName2"] = {}
        raw_request["q2_fullName2"]["first"] = row[1]
        raw_request["q2_fullName2"]["last"] = row[2]
    else:
        raw_request["input_language"] = "English (UK)"
        raw_request["q3_hiThank"] = {}
        raw_request["q3_hiThank"]["first"] = row[1]
        raw_request["q3_hiThank"]["last"] = row[2]

    raw_request["slug"] = ""
    raw_request["preview"] = False
    raw_request.update(dict(zip(q_ids[form_title], row[3:])))

    data = {
        "rawRequest" : json.dumps(raw_request),
        "formTitle" : form_title
    }
    send_data(data)

def main():
    for form in q_ids:
        filename = "./{0}.csv".format(form)
        try:
            reader = csv.reader(open(filename, "r"))
        except:
            continue

        i = 0
        for row in reader:
            if i:
                process_row(form, row)
            i += 1

if __name__ == "__main__":
    main()