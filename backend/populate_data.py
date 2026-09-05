import os
import json

DATA_DIR = r"C:\Users\adwait\.gemini\antigravity\scratch\crime-network-intelligence\data"
os.makedirs(DATA_DIR, exist_ok=True)

# 1. ENTITIES
entities_csv = """entity_id,name,age,gender,phone_number,address_location,vehicle_number,known_organization
ENT_001,Advik Maharaj,23,Male,+91 95350 39256,"27, Kapoor Ganj, Cyberabad",DL-08-SN-1520,
ENT_002,Charan Chahal,36,Male,+91 98674 36062,"140, Sami, Rajnagar",WB-02-SI-1106,BlueSky Exporters
ENT_003,Amruta Chander,43,Female,+91 95259 38221,"87, Kaul Ganj, Gopalpur",,
ENT_004,Ira Saini,44,Female,+91 95926 15695,"118, Sen Ganj, Rajnagar",RJ-14-CR-5803,Global Cargo Express
ENT_005,Aarush Dutta,26,Male,+91 98777 39871,"75, Oak Marg, Gopalpur",UP-32-DM-5554,
ENT_006,Garima Kale,32,Female,+91 91463 37460,"69, Chaudry Path, Indrapuri",DL-08-TU-3803,
ENT_007,Ranveer Chatterjee,32,Male,+91 70488 45382,"143, Padmanabhan Path, Vikramnagar",,
ENT_008,Anthony Sharaf,36,Male,+91 98924 51347,"69, Dash Circle, Shivnagar",,Global Cargo Express
ENT_009,Balveer Memon,63,Male,+91 70505 94259,"37, Pathak, Chandanpur",,
ENT_010,Bhavya Bath,59,Female,+91 88697 62350,"57, Mann Ganj, Vidyanagar",KA-03-QP-2489,Devgarh Traders
ENT_011,Jackson Chaudhuri,62,Male,+91 99911 99192,"17, Mall Marg, Shivnagar",WB-02-QI-1188,Devgarh Traders
ENT_012,Rajata Gaba,63,Female,+91 91214 48469,"41, Pant Path, Shivnagar",TS-09-QY-3927,
ENT_013,Kiaan Bora,62,Male,+91 95961 93748,"51, Garg, Suryanagar",,Apex Logistics Pvt Ltd
ENT_014,Gautami Shere,53,Female,+91 98214 57576,"79, Madan Marg, Vikramnagar",,
ENT_015,Nicholas Bhalla,27,Male,+91 70935 19071,"137, Balay Ganj, Gopalpur",KA-03-VP-3705,
ENT_016,Suhani Loyal,35,Female,+91 96830 50857,"96, Kakar Zila, Shivnagar",WB-02-DH-4681,
ENT_017,Hitesh Tata,59,Male,+91 96702 38864,"19, Shanker Marg, Devgarh",MH-12-HC-1514,Devgarh Traders
ENT_018,Kevin Dewan,39,Male,+91 70319 80678,"147, Yohannan Ganj, Cyberabad",UP-32-ZP-7669,
ENT_019,Tanish Rastogi,64,Male,+91 88462 65519,"120, Kanda Path, Shivnagar",MH-12-VU-2612,
ENT_020,Yashoda Tak,28,Female,+91 96296 34931,"115, Batta Zila, Suryanagar",,
ENT_021,Ganga Dutta,37,Female,+91 97553 82132,"13, Bhatt Marg, Anandpur",MH-12-CY-4872,
ENT_022,Sai Sidhu,52,Female,+91 96985 62565,"16, Krishnamurthy Circle, Vikramnagar",,
ENT_023,Deepa Yadav,38,Female,+91 70392 65444,"143, Oak Road, Rajnagar",WB-02-EG-5861,
ENT_024,Manan Saran,59,Male,+91 98865 51104,"13, Setty Street, Devgarh",KA-03-BQ-2312,Devgarh Traders
ENT_025,Karan Tella,65,Male,+91 96513 25713,"146, Tripathi Street, Vikramnagar",,
ENT_026,Manthan Tripathi,48,Male,+91 91367 36772,"81, Issac, Indrapuri",,
ENT_027,Ridhi Edwin,51,Female,+91 91869 19508,"118, Wali Circle, Devgarh",DL-08-CR-4492,
ENT_028,Neel Suresh,44,Male,+91 97350 58434,"41, Choudhury Nagar, Kalyanpur",TS-09-TZ-9666,
ENT_029,Nikita Khatri,64,Female,+91 97999 27601,"30, Khosla Nagar, Kalyanpur",KA-03-IJ-4450,Golden Crown Holdings
ENT_030,Chaman Sunder,54,Female,+91 70357 16658,"109, Walia Zila, Anandpur",MH-12-AK-3143,CyberTech Solutions
ENT_031,Devansh Soman,50,Male,+91 88674 11267,"20, Gandhi Circle, Anandpur",KA-03-RB-7049,
ENT_032,Siddharth Kakar,49,Male,+91 99142 50404,"11, Iyer Circle, Vidyanagar",UP-32-VH-2684,
ENT_033,Sudiksha Prakash,61,Female,+91 99342 31299,"46, Varughese Chowk, Gopalpur",MH-12-FX-6442,Shiv Shakti Real Estate
ENT_034,Darpan Kota,39,Male,+91 99906 24168,"10, Bhatt Ganj, Shivnagar",UP-32-GO-6728,
ENT_035,Advaith Karpe,36,Male,+91 98775 35313,"85, Kannan, Shivnagar",,
ENT_036,Bimala Bhargava,44,Female,+91 88795 80282,"8, Bir Ganj, Vidyanagar",,BlueSky Exporters
ENT_037,Oni Bobal,24,Female,+91 97710 66959,"81, Khanna Circle, Vidyanagar",DL-08-MS-4114,
ENT_038,Watika Kala,22,Female,+91 96472 66531,"85, Deo Circle, Anandpur",DL-08-XJ-9308,
ENT_039,Keya Solanki,42,Female,+91 88813 48752,"33, Gupta Marg, Suryanagar",,Shiv Shakti Real Estate
ENT_040,Chanakya Sankar,61,Male,+91 95515 81819,"1, Sampath Path, Mayapur",,
ENT_041,Vinaya Bhagat,51,Female,+91 70552 98555,"131, Bhat Zila, Ratanpur",KA-03-VC-5649,
ENT_042,Pallavi Chopra,27,Female,+91 96788 50687,"51, Handa Ganj, Ratanpur",,
ENT_043,Vanya Dey,61,Female,+91 97566 64321,"148, Goswami Marg, Vikramnagar",,Star Line Communications
ENT_044,Vedhika Krish,37,Female,+91 99771 10726,"28, Savant Zila, Vikramnagar",UP-32-FZ-9486,
ENT_045,Aryan Zachariah,29,Male,+91 70236 70901,"136, Chander Nagar, Indrapuri",HR-26-YO-9270,
ENT_046,Geetika Ray,32,Female,+91 70560 43972,"64, Srivastava Chowk, Gopalpur",TS-09-YY-9540,
ENT_047,Sai Bhargava,39,Male,+91 70179 47450,"70, Raghavan Street, Ratanpur",,Devgarh Traders
ENT_048,Robert Lanka,31,Male,+91 96492 30028,"55, Mangal Chowk, Rajnagar",,
ENT_049,Widisha Dubey,48,Female,+91 98311 65069,"150, Minhas Ganj, Shivnagar",MH-12-YS-7232,
ENT_050,Barkha Bhat,41,Female,+91 88973 64921,"140, Bhandari Path, Suryanagar",UP-32-PH-5471,
ENT_051,William Thakkar,46,Male,+91 91784 99016,"104, Dugar Circle, Gopalpur",WB-02-ET-9751,
ENT_052,Yashoda Buch,59,Female,+91 98185 94246,"35, Biswas Street, Shivnagar",KA-03-BI-7211,
ENT_053,Kamya Raval,42,Female,+91 91879 59692,"108, Koshy Zila, Kalyanpur",,
ENT_054,Banjeet Saini,56,Male,+91 98458 39389,"18, Virk, Indrapuri",MH-12-YA-5051,
ENT_055,Kalpit Jayaraman,61,Male,+91 99344 26544,"30, Khare Path, Chandanpur",UP-32-OW-5198,BlueSky Exporters
ENT_056,Rudra Deep,32,Male,+91 95210 85849,"80, Shankar Road, Devgarh",RJ-14-MW-4249,
ENT_057,Balhaar Andra,28,Male,+91 95970 99687,"31, Chaudhry Chowk, Navgram",MH-12-LR-8018,Devgarh Traders
ENT_058,Jalsa Toor,22,Female,+91 88942 74251,"111, Deo Road, Anandpur",WB-02-WE-8135,
ENT_059,Bhavya Konda,61,Female,+91 70576 67091,"69, Mane Path, Mayapur",,
ENT_060,Theodore Mittal,39,Male,+91 70349 70910,"98, Wadhwa, Navgram",,
ENT_061,Netra Chawla,33,Female,+91 70317 56507,"67, Lalla Street, Gopalpur",,CyberTech Solutions
ENT_062,Chatresh Dugal,55,Male,+91 96187 41635,"105, Manda Road, Rajnagar",UP-32-WP-9041,
ENT_063,Onveer Jani,27,Male,+91 95326 63005,"63, Tiwari Road, Rajnagar",,
ENT_064,Ladli Behl,57,Female,+91 91535 82140,"91, Sampath Zila, Vidyanagar",TS-09-JI-4777,
ENT_065,Anthony Aggarwal,42,Male,+91 97860 80236,"48, De Path, Gopalpur",,CyberTech Solutions
ENT_066,Gaurika Sathe,28,Female,+91 96403 39816,"46, Sane Circle, Vidyanagar",,BlueSky Exporters
ENT_067,Dayita Borra,24,Female,+91 98666 48290,"33, Banik Street, Rajnagar",WB-02-DA-5658,
ENT_068,Falak Sani,43,Female,+91 99152 43092,"123, Barman Street, Mayapur",,
ENT_069,Rajata Baral,26,Female,+91 98255 29555,"145, Kade Path, Gopalpur",DL-08-HD-7818,Golden Crown Holdings
ENT_070,Dalaja Pandya,50,Female,+91 70404 87139,"79, Ray Circle, Shivnagar",MH-12-TX-2625,Golden Crown Holdings
ENT_071,Jagat Gaba,38,Male,+91 97260 41439,"142, Sachar Street, Cyberabad",,
ENT_072,Hemal Natarajan,60,Female,+91 70398 14278,"74, Kothari Marg, Ratanpur",WB-02-CV-4824,Golden Crown Holdings
ENT_073,Gauri Chokshi,29,Female,+91 96763 29528,"69, Barad Marg, Vikramnagar",DL-08-BF-6039,
ENT_074,Janya Iyengar,50,Female,+91 97579 49857,"104, Palla Chowk, Rajnagar",WB-02-OC-1653,Global Cargo Express
ENT_075,Jhalak Kapoor,23,Female,+91 97334 98381,"148, Hans Nagar, Mayapur",MH-12-YV-5415,
"""

with open(os.path.join(DATA_DIR, "entities.csv"), "w", encoding="utf-8") as f:
    f.write(entities_csv.strip() + "\n")
print("Wrote entities.csv")

# 2. CRIMINAL RECORDS
crim_csv = """record_id,entity_id,prior_case_id,offense_type,date,status
CRIM_REC_001,ENT_011,CASE_2024_490,Section 420 IPC (Cheating & Fraud),2024-06-18,Convicted (Bail)
CRIM_REC_002,ENT_012,CASE_2021_456,Arms Act Section 25 (Unlawful Arms),2021-10-01,Absconding / Wanted
CRIM_REC_003,ENT_014,CASE_2019_990,Section 307 IPC (Attempted Extortion),2019-05-09,Convicted (Bail)
CRIM_REC_004,ENT_019,CASE_2022_155,NDPS Act Section 21 (Narcotics Smuggling),2022-04-16,Convicted (Bail)
CRIM_REC_005,ENT_021,CASE_2021_652,IT Act Section 66D (Cyber Impersonation),2021-07-31,Pending Trial
CRIM_REC_006,ENT_025,CASE_2021_614,Section 120B IPC (Criminal Conspiracy),2021-08-31,Pending Trial
CRIM_REC_007,ENT_008,CASE_2019_151,Section 120B IPC (Criminal Conspiracy),2019-09-20,Absconding / Wanted
CRIM_REC_008,ENT_001,CASE_2022_870,IT Act Section 66D (Cyber Impersonation),2022-12-31,Convicted (Bail)
CRIM_REC_009,ENT_020,CASE_2020_542,NDPS Act Section 21 (Narcotics Smuggling),2020-06-28,Absconding / Wanted
CRIM_REC_010,ENT_005,CASE_2019_235,NDPS Act Section 21 (Narcotics Smuggling),2019-08-30,Convicted (Bail)
CRIM_REC_011,ENT_003,CASE_2023_685,Section 120B IPC (Criminal Conspiracy),2023-05-04,Convicted (Bail)
CRIM_REC_012,ENT_018,CASE_2024_508,NDPS Act Section 21 (Narcotics Smuggling),2024-02-24,Convicted (Bail)
CRIM_REC_013,ENT_024,CASE_2022_613,Arms Act Section 25 (Unlawful Arms),2022-06-21,Pending Trial
CRIM_REC_014,ENT_007,CASE_2019_592,IT Act Section 66D (Cyber Impersonation),2019-07-07,Pending Trial
CRIM_REC_015,ENT_002,CASE_2023_504,Section 120B IPC (Criminal Conspiracy),2023-06-22,Pending Trial
CRIM_REC_016,ENT_022,CASE_2024_730,Section 120B IPC (Criminal Conspiracy),2024-04-17,Pending Trial
CRIM_REC_017,ENT_013,CASE_2020_173,NDPS Act Section 21 (Narcotics Smuggling),2020-09-19,Absconding / Wanted
CRIM_REC_018,ENT_009,CASE_2021_801,IT Act Section 66D (Cyber Impersonation),2021-08-17,Convicted (Bail)
CRIM_REC_019,ENT_026,CASE_2019_787,Arms Act Section 25 (Unlawful Arms),2019-04-06,Absconding / Wanted
CRIM_REC_020,ENT_004,CASE_2022_456,Section 307 IPC (Attempted Extortion),2022-02-05,Acquitted
"""
with open(os.path.join(DATA_DIR, "criminal_records.csv"), "w", encoding="utf-8") as f:
    f.write(crim_csv.strip() + "\n")
print("Wrote criminal_records.csv")

# 3. SOCIAL MEDIA POSTS
posts_csv = """post_id,author_entity_id,timestamp,platform,text
POST_001,ENT_022,2026-05-17 00:37:00,InstaNet,Package arrived at Vikramnagar warehouse. Awaiting signal from Advik to dispatch.
POST_002,ENT_001,2026-05-16 19:44:00,InstaNet,New SIM batches ready. Contact @Advik_Maharaj for login keys.
POST_003,ENT_013,2026-05-07 18:14:00,InstaNet,Big consignment moving across highway checkpoint at 02:00.
POST_004,ENT_067,2026-05-09 10:44:00,InstaNet,New SIM batches ready. Contact @Dayita_Borra for login keys.
POST_005,ENT_012,2026-05-30 07:30:00,X-Feed,Big consignment moving across highway checkpoint at 02:00.
POST_006,ENT_025,2026-07-10 13:10:00,Chatgram,Meeting scheduled at Vikramnagar tonight with team. Bring vehicle MH-12-AB-1234.
POST_007,ENT_012,2026-05-07 16:15:00,DarkPost,Package arrived at Shivnagar warehouse. Awaiting signal from Advik to dispatch.
POST_008,ENT_028,2026-04-22 01:24:00,X-Feed,Big consignment moving across highway checkpoint at 02:00.
POST_009,ENT_004,2026-05-01 23:13:00,DarkPost,Cash collected from Devgarh outlet. Heading to safehouse.
POST_010,ENT_011,2026-05-15 18:05:00,Chatgram,Package arrived at Shivnagar warehouse. Awaiting signal from Advik to dispatch.
POST_011,ENT_009,2026-06-27 00:30:00,X-Feed,Meeting scheduled at Chandanpur tonight with team. Bring vehicle MH-12-AB-1234.
POST_012,ENT_032,2026-04-30 05:00:00,InstaNet,Package arrived at Vidyanagar warehouse. Awaiting signal from Advik to dispatch.
POST_013,ENT_020,2026-04-12 10:23:00,Chatgram,Meeting scheduled at Suryanagar tonight with team. Bring vehicle MH-12-AB-1234.
POST_014,ENT_009,2026-07-08 03:22:00,Chatgram,Transfer settled on UPI. Confirm receipt for consignment #8821.
POST_015,ENT_020,2026-07-12 03:29:00,DarkPost,New SIM batches ready. Contact @Yashoda_Tak for login keys.
POST_016,ENT_004,2026-06-09 06:30:00,DarkPost,Big consignment moving across highway checkpoint at 02:00.
POST_017,ENT_013,2026-06-28 20:20:00,InstaNet,Cash collected from Devgarh outlet. Heading to safehouse.
POST_018,ENT_009,2026-06-29 17:15:00,X-Feed,Cash collected from Devgarh outlet. Heading to safehouse.
POST_019,ENT_007,2026-05-30 10:11:00,InstaNet,Meeting scheduled at Vikramnagar tonight with team. Bring vehicle MH-12-AB-1234.
POST_020,ENT_071,2026-04-30 16:34:00,Chatgram,Cash collected from Devgarh outlet. Heading to safehouse.
POST_021,ENT_012,2026-05-19 10:36:00,DarkPost,New SIM batches ready. Contact @Rajata_Gaba for login keys.
POST_022,ENT_015,2026-07-02 14:34:00,InstaNet,Big consignment moving across highway checkpoint at 02:00.
POST_023,ENT_004,2026-06-06 18:41:00,X-Feed,Meeting scheduled at Rajnagar tonight with team. Bring vehicle RJ-14-CR-5803.
POST_024,ENT_027,2026-07-08 14:45:00,InstaNet,Transfer settled on UPI. Confirm receipt for consignment #8821.
POST_025,ENT_005,2026-07-10 21:24:00,X-Feed,Cash collected from Devgarh outlet. Heading to safehouse.
POST_026,ENT_024,2026-05-30 02:57:00,Chatgram,Package arrived at Devgarh warehouse. Awaiting signal from Advik to dispatch.
POST_027,ENT_014,2026-04-09 11:16:00,X-Feed,Transfer settled on UPI. Confirm receipt for consignment #8821.
POST_028,ENT_026,2026-04-20 23:44:00,InstaNet,Transfer settled on UPI. Confirm receipt for consignment #8821.
POST_029,ENT_019,2026-06-11 05:49:00,InstaNet,Cash collected from Devgarh outlet. Heading to safehouse.
POST_030,ENT_019,2026-05-18 02:13:00,Chatgram,Meeting scheduled at Shivnagar tonight with team. Bring vehicle MH-12-VU-2612.
POST_031,ENT_009,2026-04-14 09:40:00,Chatgram,Transfer settled on UPI. Confirm receipt for consignment #8821.
POST_032,ENT_022,2026-04-16 01:21:00,InstaNet,Big consignment moving across highway checkpoint at 02:00.
POST_033,ENT_018,2026-06-16 05:20:00,DarkPost,Big consignment moving across highway checkpoint at 02:00.
POST_034,ENT_006,2026-05-19 21:22:00,Chatgram,Big consignment moving across highway checkpoint at 02:00.
POST_035,ENT_012,2026-04-15 16:31:00,X-Feed,Cash collected from Devgarh outlet. Heading to safehouse.
POST_036,ENT_025,2026-05-13 13:20:00,InstaNet,Transfer settled on UPI. Confirm receipt for consignment #8821.
POST_037,ENT_027,2026-05-16 18:52:00,X-Feed,Cash collected from Devgarh outlet. Heading to safehouse.
POST_038,ENT_024,2026-04-20 17:00:00,DarkPost,Big consignment moving across highway checkpoint at 02:00.
POST_039,ENT_027,2026-06-18 05:56:00,Chatgram,Transfer settled on UPI. Confirm receipt for consignment #8821.
POST_040,ENT_071,2026-06-13 14:26:00,DarkPost,Big consignment moving across highway checkpoint at 02:00.
POST_041,ENT_006,2026-06-21 03:33:00,DarkPost,Meeting scheduled at Indrapuri tonight with team. Bring vehicle DL-08-TU-3803.
POST_042,ENT_020,2026-06-08 04:05:00,InstaNet,Big consignment moving across highway checkpoint at 02:00.
POST_043,ENT_025,2026-05-30 09:11:00,X-Feed,Cash collected from Devgarh outlet. Heading to safehouse.
POST_044,ENT_021,2026-07-10 16:02:00,DarkPost,Meeting scheduled at Anandpur tonight with team. Bring vehicle MH-12-CY-4872.
POST_045,ENT_058,2026-06-12 18:55:00,Chatgram,Big consignment moving across highway checkpoint at 02:00.
POST_046,ENT_012,2026-04-04 11:14:00,X-Feed,Meeting scheduled at Shivnagar tonight with team. Bring vehicle TS-09-QY-3927.
POST_047,ENT_023,2026-05-10 14:35:00,DarkPost,Package arrived at Rajnagar warehouse. Awaiting signal from Advik to dispatch.
POST_048,ENT_036,2026-07-11 07:00:00,X-Feed,Package arrived at Vidyanagar warehouse. Awaiting signal from Advik to dispatch.
POST_049,ENT_007,2026-04-29 22:03:00,X-Feed,Meeting scheduled at Vikramnagar tonight with team. Bring vehicle MH-12-AB-1234.
POST_050,ENT_019,2026-05-16 23:39:00,X-Feed,Meeting scheduled at Shivnagar tonight with team. Bring vehicle MH-12-VU-2612.
"""
with open(os.path.join(DATA_DIR, "social_media_posts.csv"), "w", encoding="utf-8") as f:
    f.write(posts_csv.strip() + "\n")
print("Wrote social_media_posts.csv")

# 4. FIRS
firs_csv = """fir_id,date,police_station,incident_type,narrative_text
FIR_2026_001,2026-07-15,Ratanpur Crime Branch,Identity Theft & Fake SIMs,Investigative audit by Ratanpur Crime Branch exposed a cyber phishing syndicate operating in Chandanpur. Key operative Balveer Memon (Phone: +91 70505 94259) acquired fraudulent SIM cards with assistance from Deepa Yadav. Money trail traced multiple UPI transactions to account registered under Apex Logistics.
FIR_2026_002,2026-03-13,Ratanpur Crime Branch,Organized Retail Fraud,Investigative audit by Ratanpur Crime Branch exposed a cyber phishing syndicate operating in Cyberabad. Key operative Advik Maharaj (Phone: +91 95350 39256) acquired fraudulent SIM cards with assistance from Charan Chahal. Money trail traced multiple UPI transactions to account registered under Apex Logistics.
FIR_2026_003,2026-01-24,Vidyanagar North PS,Vehicle Theft & Smuggling,A formal FIR was registered regarding extortion calls received by local businessmen in Suryanagar. The caller identified himself under an alias connected to Kiaan Bora. Intercept analysis identified accomplice Charan Chahal using vehicle WB-02-SI-1106 to collect cash packages. Bank statements reveal funds routed to Apex Logistics Pvt Ltd.
FIR_2026_004,2026-06-21,Devgarh Central PS,Narcotics Smuggling,Surveillance unit at Devgarh Central PS logged suspicious meeting at Devgarh involving known subject Ridhi Edwin and associate Manan Saran. Vehicle DL-08-CR-4492 was parked nearby. Intelligence report indicates discussion centered on money laundering operations via Apex Logistics.
FIR_2026_005,2026-05-07,Kalyanpur Anti-Narcotics Cell,Organized Retail Fraud,Special task force operation at Navgram seized unauthorized firearms and ammunition. Suspect Balhaar Andra was detained at the scene. Interrogation transcript indicates firearms were supplied by Gaurika Sathe (Phone: +91 96403 39816) using transport registered under vehicle MH-12-LR-8018.
FIR_2026_006,2026-01-10,Vidyanagar North PS,Hawala Money Laundering,A formal FIR was registered regarding extortion calls received by local businessmen in Rajnagar. The caller identified himself under an alias connected to Deepa Yadav. Intercept analysis identified accomplice Bhavya Bath using vehicle KA-03-QP-2489 to collect cash packages. Bank statements reveal funds routed to Apex Logistics.
FIR_2026_007,2026-01-30,Suryanagar Crime Investigation Unit,Cyber Fraud & Phishing,Special task force operation at Shivnagar seized unauthorized firearms and ammunition. Suspect Tanish Rastogi was detained at the scene. Interrogation transcript indicates firearms were supplied by Karan Tella (Phone: +91 96513 25713) using transport registered under vehicle MH-12-VU-2612.
FIR_2026_008,2026-04-29,Suryanagar Crime Investigation Unit,Cyber Fraud & Phishing,A formal FIR was registered regarding extortion calls received by local businessmen in Cyberabad. The caller identified himself under an alias connected to Kevin Dewan. Intercept analysis identified accomplice Nicholas Bhalla using vehicle KA-03-VP-3705 to collect cash packages. Bank statements reveal funds routed to Apex Logistics.
FIR_2026_009,2026-06-09,Vidyanagar North PS,Identity Theft & Fake SIMs,Police raid conducted near Anandpur under Vidyanagar North PS jurisdiction following an anonymous tip. Officers intercepted vehicle KA-03-RB-7049 driven by Devansh Soman. Search yielded suspicious contraband and documents belonging to Apex Logistics. Phone records show frequent contact between Devansh Soman (+91 88674 11267) and Gauri Chokshi (+91 96763 29528) prior to the trip.
FIR_2026_010,2026-03-10,Ratanpur Crime Branch,Illegal Firearms Possession,Surveillance unit at Ratanpur Crime Branch logged suspicious meeting at Shivnagar involving known subject Rajata Gaba and associate Ranveer Chatterjee. Vehicle TS-09-QY-3927 was parked nearby. Intelligence report indicates discussion centered on money laundering operations via Apex Logistics.
FIR_2026_011,2026-05-05,Devgarh Central PS,Cyber Fraud & Phishing,Special task force operation at Shivnagar seized unauthorized firearms and ammunition. Suspect Rajata Gaba was detained at the scene. Interrogation transcript indicates firearms were supplied by Chatresh Dugal (Phone: +91 96187 41635) using transport registered under vehicle TS-09-QY-3927.
FIR_2026_012,2026-07-24,Anandpur Sector-4 PS,Narcotics Smuggling,"On 24-Jul-2026, complainant reported a financial fraud incident at Anandpur Sector-4 PS. Investigation revealed that suspect Ridhi Edwin (Phone: +91 91869 19508) operating from Devgarh facilitated illegal wire transfers. Suspect was spotted driving vehicle DL-08-CR-4492 along with associate Anthony Sharaf (Phone: +91 98924 51347). Further intelligence links them to Apex Logistics."
FIR_2026_013,2026-05-22,Suryanagar Crime Investigation Unit,Hawala Money Laundering,"On 22-May-2026, complainant reported a financial fraud incident at Suryanagar Crime Investigation Unit. Investigation revealed that suspect Ganga Dutta (Phone: +91 97553 82132) operating from Anandpur facilitated illegal wire transfers. Suspect was spotted driving vehicle MH-12-CY-4872 along with associate Kiaan Bora (Phone: +91 95961 93748). Further intelligence links them to Apex Logistics."
FIR_2026_014,2026-04-29,Devgarh Central PS,Narcotics Smuggling,Surveillance unit at Devgarh Central PS logged suspicious meeting at Devgarh involving known subject Manan Saran and associate Suhani Loyal. Vehicle KA-03-BQ-2312 was parked nearby. Intelligence report indicates discussion centered on money laundering operations via Devgarh Traders.
FIR_2026_015,2026-03-16,Kalyanpur Anti-Narcotics Cell,Organized Retail Fraud,Investigative audit by Kalyanpur Anti-Narcotics Cell exposed a cyber phishing syndicate operating in Gopalpur. Key operative Netra Chawla (Phone: +91 70317 56507) acquired fraudulent SIM cards with assistance from Sai Sidhu. Money trail traced multiple UPI transactions to account registered under CyberTech Solutions.
FIR_2026_016,2026-03-04,Vidyanagar North PS,Narcotics Smuggling,Special task force operation at Shivnagar seized unauthorized firearms and ammunition. Suspect Jackson Chaudhuri was detained at the scene. Interrogation transcript indicates firearms were supplied by Suhani Loyal (Phone: +91 96830 50857) using transport registered under vehicle WB-02-QI-1188.
FIR_2026_017,2026-05-11,Ratanpur Crime Branch,Hawala Money Laundering,Investigative audit by Ratanpur Crime Branch exposed a cyber phishing syndicate operating in Rajnagar. Key operative Ira Saini (Phone: +91 95926 15695) acquired fraudulent SIM cards with assistance from Yashoda Tak. Money trail traced multiple UPI transactions to account registered under Global Cargo Express.
FIR_2026_018,2026-03-29,Kalyanpur Anti-Narcotics Cell,Cyber Fraud & Phishing,A formal FIR was registered regarding extortion calls received by local businessmen in Devgarh. The caller identified himself under an alias connected to Ridhi Edwin. Intercept analysis identified accomplice Manan Saran using vehicle KA-03-BQ-2312 to collect cash packages. Bank statements reveal funds routed to Apex Logistics.
FIR_2026_019,2026-08-03,Vidyanagar North PS,Narcotics Smuggling,Investigative audit by Vidyanagar North PS exposed a cyber phishing syndicate operating in Devgarh. Key operative Ridhi Edwin (Phone: +91 91869 19508) acquired fraudulent SIM cards with assistance from Tanish Rastogi. Money trail traced multiple UPI transactions to account registered under Apex Logistics.
FIR_2026_020,2026-03-30,"Special Task Force HQ, Indrapuri",Organized Retail Fraud,A formal FIR was registered regarding extortion calls received by local businessmen in Indrapuri. The caller identified himself under an alias connected to Manthan Tripathi. Intercept analysis identified accomplice Kiaan Bora using vehicle DL-08-YY-8888 to collect cash packages. Bank statements reveal funds routed to Apex Logistics.
FIR_2026_021,2026-02-18,Anandpur Sector-4 PS,Organized Retail Fraud,Investigative audit by Anandpur Sector-4 PS exposed a cyber phishing syndicate operating in Suryanagar. Key operative Kiaan Bora (Phone: +91 95961 93748) acquired fraudulent SIM cards with assistance from Amruta Chander. Money trail traced multiple UPI transactions to account registered under Apex Logistics Pvt Ltd.
FIR_2026_022,2026-01-12,"Special Task Force HQ, Indrapuri",Identity Theft & Fake SIMs,"Investigative audit by Special Task Force HQ, Indrapuri exposed a cyber phishing syndicate operating in Kalyanpur. Key operative Kamya Raval (Phone: +91 91879 59692) acquired fraudulent SIM cards with assistance from Banjeet Saini. Money trail traced multiple UPI transactions to account registered under Apex Logistics."
FIR_2026_023,2026-04-09,Ratanpur Crime Branch,Identity Theft & Fake SIMs,Police raid conducted near Vikramnagar under Ratanpur Crime Branch jurisdiction following an anonymous tip. Officers intercepted vehicle UP-32-FZ-9486 driven by Vedhika Krish. Search yielded suspicious contraband and documents belonging to Apex Logistics. Phone records show frequent contact between Vedhika Krish (+91 99771 10726) and Devansh Soman (+91 88674 11267) prior to the trip.
FIR_2026_024,2026-05-09,"Special Task Force HQ, Indrapuri",Hawala Money Laundering,"Investigative audit by Special Task Force HQ, Indrapuri exposed a cyber phishing syndicate operating in Gopalpur. Key operative Aarush Dutta (Phone: +91 98777 39871) acquired fraudulent SIM cards with assistance from Ganga Dutta. Money trail traced multiple UPI transactions to account registered under Apex Logistics."
FIR_2026_025,2026-01-26,Vidyanagar North PS,Cyber Fraud & Phishing,Investigative audit by Vidyanagar North PS exposed a cyber phishing syndicate operating in Devgarh. Key operative Ridhi Edwin (Phone: +91 91869 19508) acquired fraudulent SIM cards with assistance from Jhalak Kapoor. Money trail traced multiple UPI transactions to account registered under Apex Logistics.
FIR_2026_026,2026-06-17,Ratanpur Crime Branch,Hawala Money Laundering,A formal FIR was registered regarding extortion calls received by local businessmen in Indrapuri. The caller identified himself under an alias connected to Manthan Tripathi. Intercept analysis identified accomplice Manthan Tripathi using vehicle DL-08-YY-8888 to collect cash packages. Bank statements reveal funds routed to Apex Logistics.
FIR_2026_027,2026-03-28,Suryanagar Crime Investigation Unit,Hawala Money Laundering,Surveillance unit at Suryanagar Crime Investigation Unit logged suspicious meeting at Vidyanagar involving known subject Gaurika Sathe and associate Jhalak Kapoor. Vehicle MH-12-XX-9999 was parked nearby. Intelligence report indicates discussion centered on money laundering operations via BlueSky Exporters.
FIR_2026_028,2026-08-08,Suryanagar Crime Investigation Unit,Vehicle Theft & Smuggling,Investigative audit by Suryanagar Crime Investigation Unit exposed a cyber phishing syndicate operating in Shivnagar. Key operative Anthony Sharaf (Phone: +91 98924 51347) acquired fraudulent SIM cards with assistance from Charan Chahal. Money trail traced multiple UPI transactions to account registered under Global Cargo Express.
FIR_2026_029,2026-05-19,"Cyber Crime PS, Cyberabad",Hawala Money Laundering,"Surveillance unit at Cyber Crime PS, Cyberabad logged suspicious meeting at Chandanpur involving known subject Balveer Memon and associate Jackson Chaudhuri. Vehicle MH-12-XX-9999 was parked nearby. Intelligence report indicates discussion centered on money laundering operations via Apex Logistics."
FIR_2026_030,2026-03-15,Anandpur Sector-4 PS,Hawala Money Laundering,"On 15-Mar-2026, complainant reported a financial fraud incident at Anandpur Sector-4 PS. Investigation revealed that suspect Tanish Rastogi (Phone: +91 88462 65519) operating from Shivnagar facilitated illegal wire transfers. Suspect was spotted driving vehicle MH-12-VU-2612 along with associate Gautami Shere (Phone: +91 98214 57576). Further intelligence links them to Apex Logistics."
FIR_2026_031,2026-07-14,Devgarh Central PS,Identity Theft & Fake SIMs,A formal FIR was registered regarding extortion calls received by local businessmen in Vikramnagar. The caller identified himself under an alias connected to Karan Tella. Intercept analysis identified accomplice Deepa Yadav using vehicle WB-02-EG-5861 to collect cash packages. Bank statements reveal funds routed to Apex Logistics.
FIR_2026_032,2026-01-08,"Cyber Crime PS, Cyberabad",Vehicle Theft & Smuggling,A formal FIR was registered regarding extortion calls received by local businessmen in Ratanpur. The caller identified himself under an alias connected to Pallavi Chopra. Intercept analysis identified accomplice Devansh Soman using vehicle KA-03-RB-7049 to collect cash packages. Bank statements reveal funds routed to Apex Logistics.
FIR_2026_033,2026-04-02,"Special Task Force HQ, Indrapuri",Organized Retail Fraud,Special task force operation at Devgarh seized unauthorized firearms and ammunition. Suspect Manan Saran was detained at the scene. Interrogation transcript indicates firearms were supplied by Ridhi Edwin (Phone: +91 91869 19508) using transport registered under vehicle KA-03-BQ-2312.
FIR_2026_034,2026-04-16,Ratanpur Crime Branch,Narcotics Smuggling,Special task force operation at Vikramnagar seized unauthorized firearms and ammunition. Suspect Sai Sidhu was detained at the scene. Interrogation transcript indicates firearms were supplied by Gautami Shere (Phone: +91 98214 57576) using transport registered under vehicle MH-12-XX-9999.
FIR_2026_035,2026-04-08,Anandpur Sector-4 PS,Identity Theft & Fake SIMs,Police raid conducted near Devgarh under Anandpur Sector-4 PS jurisdiction following an anonymous tip. Officers intercepted vehicle RJ-14-MW-4249 driven by Rudra Deep. Search yielded suspicious contraband and documents belonging to Apex Logistics. Phone records show frequent contact between Rudra Deep (+91 95210 85849) and Netra Chawla (+91 70317 56507) prior to the trip.
FIR_2026_036,2026-03-01,Vidyanagar North PS,Illegal Firearms Possession,Surveillance unit at Vidyanagar North PS logged suspicious meeting at Gopalpur involving known subject Amruta Chander and associate Kiaan Bora. Vehicle MH-12-XX-9999 was parked nearby. Intelligence report indicates discussion centered on money laundering operations via Apex Logistics.
FIR_2026_037,2026-01-03,Vidyanagar North PS,Illegal Firearms Possession,Police raid conducted near Rajnagar under Vidyanagar North PS jurisdiction following an anonymous tip. Officers intercepted vehicle RJ-14-CR-5803 driven by Ira Saini. Search yielded suspicious contraband and documents belonging to Global Cargo Express. Phone records show frequent contact between Ira Saini (+91 95926 15695) and Ridhi Edwin (+91 91869 19508) prior to the trip.
FIR_2026_038,2026-01-19,Vidyanagar North PS,Vehicle Theft & Smuggling,A formal FIR was registered regarding extortion calls received by local businessmen in Mayapur. The caller identified himself under an alias connected to Jhalak Kapoor. Intercept analysis identified accomplice Chanakya Sankar using vehicle DL-08-YY-8888 to collect cash packages. Bank statements reveal funds routed to Apex Logistics.
FIR_2026_039,2026-06-13,Suryanagar Crime Investigation Unit,Illegal Firearms Possession,A formal FIR was registered regarding extortion calls received by local businessmen in Shivnagar. The caller identified himself under an alias connected to Tanish Rastogi. Intercept analysis identified accomplice Manan Saran using vehicle KA-03-BQ-2312 to collect cash packages. Bank statements reveal funds routed to Apex Logistics.
FIR_2026_040,2026-02-20,Suryanagar Crime Investigation Unit,Identity Theft & Fake SIMs,Investigative audit by Suryanagar Crime Investigation Unit exposed a cyber phishing syndicate operating in Vidyanagar. Key operative Bhavya Bath (Phone: +91 88697 62350) acquired fraudulent SIM cards with assistance from Nicholas Bhalla. Money trail traced multiple UPI transactions to account registered under Devgarh Traders.
FIR_2026_041,2026-05-27,"Special Task Force HQ, Indrapuri",Illegal Firearms Possession,A formal FIR was registered regarding extortion calls received by local businessmen in Gopalpur. The caller identified himself under an alias connected to Aarush Dutta. Intercept analysis identified accomplice Jagat Gaba using vehicle DL-08-YY-8888 to collect cash packages. Bank statements reveal funds routed to Apex Logistics.
FIR_2026_042,2026-01-06,Suryanagar Crime Investigation Unit,Illegal Firearms Possession,Surveillance unit at Suryanagar Crime Investigation Unit logged suspicious meeting at Shivnagar involving known subject Suhani Loyal and associate Gautami Shere. Vehicle WB-02-DH-4681 was parked nearby. Intelligence report indicates discussion centered on money laundering operations via Apex Logistics.
FIR_2026_043,2026-07-19,"Cyber Crime PS, Cyberabad",Identity Theft & Fake SIMs,A formal FIR was registered regarding extortion calls received by local businessmen in Vikramnagar. The caller identified himself under an alias connected to Vedhika Krish. Intercept analysis identified accomplice Hemal Natarajan using vehicle WB-02-CV-4824 to collect cash packages. Bank statements reveal funds routed to Apex Logistics.
FIR_2026_044,2026-07-18,Anandpur Sector-4 PS,Vehicle Theft & Smuggling,Police raid conducted near Vidyanagar under Anandpur Sector-4 PS jurisdiction following an anonymous tip. Officers intercepted vehicle KA-03-QP-2489 driven by Bhavya Bath. Search yielded suspicious contraband and documents belonging to Devgarh Traders. Phone records show frequent contact between Bhavya Bath (+91 88697 62350) and Ranveer Chatterjee (+91 70488 45382) prior to the trip.
FIR_2026_045,2026-06-08,Kalyanpur Anti-Narcotics Cell,Narcotics Smuggling,Surveillance unit at Kalyanpur Anti-Narcotics Cell logged suspicious meeting at Indrapuri involving known subject Garima Kale and associate Bhavya Bath. Vehicle DL-08-TU-3803 was parked nearby. Intelligence report indicates discussion centered on money laundering operations via Apex Logistics.
FIR_2026_046,2026-06-15,"Cyber Crime PS, Cyberabad",Illegal Firearms Possession,"On 15-Jun-2026, complainant reported a financial fraud incident at Cyber Crime PS, Cyberabad. Investigation revealed that suspect Advaith Karpe (Phone: +91 98775 35313) operating from Shivnagar facilitated illegal wire transfers. Suspect was spotted driving vehicle MH-12-XX-9999 along with associate Robert Lanka (Phone: +91 96492 30028). Further intelligence links them to Apex Logistics."
FIR_2026_047,2026-05-29,"Special Task Force HQ, Indrapuri",Narcotics Smuggling,A formal FIR was registered regarding extortion calls received by local businessmen in Vikramnagar. The caller identified himself under an alias connected to Sai Sidhu. Intercept analysis identified accomplice Suhani Loyal using vehicle WB-02-DH-4681 to collect cash packages. Bank statements reveal funds routed to Apex Logistics.
FIR_2026_048,2026-03-25,Suryanagar Crime Investigation Unit,Narcotics Smuggling,Special task force operation at Cyberabad seized unauthorized firearms and ammunition. Suspect Kevin Dewan was detained at the scene. Interrogation transcript indicates firearms were supplied by Charan Chahal (Phone: +91 98674 36062) using transport registered under vehicle UP-32-ZP-7669.
FIR_2026_049,2026-04-04,Kalyanpur Anti-Narcotics Cell,Narcotics Smuggling,Investigative audit by Kalyanpur Anti-Narcotics Cell exposed a cyber phishing syndicate operating in Anandpur. Key operative Ganga Dutta (Phone: +91 97553 82132) acquired fraudulent SIM cards with assistance from Amruta Chander. Money trail traced multiple UPI transactions to account registered under Apex Logistics.
FIR_2026_050,2026-07-26,Kalyanpur Anti-Narcotics Cell,Vehicle Theft & Smuggling,Investigative audit by Kalyanpur Anti-Narcotics Cell exposed a cyber phishing syndicate operating in Suryanagar. Key operative Yashoda Tak (Phone: +91 96296 34931) acquired fraudulent SIM cards with assistance from Deepa Yadav. Money trail traced multiple UPI transactions to account registered under Apex Logistics.
"""
with open(os.path.join(DATA_DIR, "firs.csv"), "w", encoding="utf-8") as f:
    f.write(firs_csv.strip() + "\n")
print("Wrote firs.csv")

# 5. GROUND TRUTH JSON
ground_truth = {
  "ENT_001": {
    "name": "Advik Maharaj",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_ALPHA"
    ],
    "primary_role": "Kingpin / Ring Leader",
    "network_roles": {
      "NET_ALPHA": "Kingpin / Ring Leader"
    }
  },
  "ENT_002": {
    "name": "Charan Chahal",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_ALPHA"
    ],
    "primary_role": "Key Lieutenant",
    "network_roles": {
      "NET_ALPHA": "Key Lieutenant"
    }
  },
  "ENT_003": {
    "name": "Amruta Chander",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_ALPHA"
    ],
    "primary_role": "Hawala Broker",
    "network_roles": {
      "NET_ALPHA": "Hawala Broker"
    }
  },
  "ENT_004": {
    "name": "Ira Saini",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_ALPHA"
    ],
    "primary_role": "Financial Mule",
    "network_roles": {
      "NET_ALPHA": "Financial Mule"
    }
  },
  "ENT_005": {
    "name": "Aarush Dutta",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_ALPHA"
    ],
    "primary_role": "Financial Mule",
    "network_roles": {
      "NET_ALPHA": "Financial Mule"
    }
  },
  "ENT_006": {
    "name": "Garima Kale",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_ALPHA"
    ],
    "primary_role": "Shell Company Director",
    "network_roles": {
      "NET_ALPHA": "Shell Company Director"
    }
  },
  "ENT_007": {
    "name": "Ranveer Chatterjee",
    "is_criminal": True,
    "is_bridge": True,
    "networks": [
      "NET_ALPHA",
      "NET_BETA"
    ],
    "primary_role": "Cross-Network Bridge Connector",
    "network_roles": {
      "NET_ALPHA": "Bridge Connector (Hawala Conduit)",
      "NET_BETA": "Bridge Connector (Money Handler)"
    }
  },
  "ENT_008": {
    "name": "Anthony Sharaf",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_ALPHA"
    ],
    "primary_role": "Operative",
    "network_roles": {
      "NET_ALPHA": "Operative"
    }
  },
  "ENT_009": {
    "name": "Balveer Memon",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_BETA"
    ],
    "primary_role": "Kingpin / Cartel Boss",
    "network_roles": {
      "NET_BETA": "Kingpin / Cartel Boss"
    }
  },
  "ENT_010": {
    "name": "Bhavya Bath",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_BETA"
    ],
    "primary_role": "Logistics Coordinator",
    "network_roles": {
      "NET_BETA": "Logistics Coordinator"
    }
  },
  "ENT_011": {
    "name": "Jackson Chaudhuri",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_BETA"
    ],
    "primary_role": "Warehouse Manager",
    "network_roles": {
      "NET_BETA": "Warehouse Manager"
    }
  },
  "ENT_012": {
    "name": "Rajata Gaba",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_BETA"
    ],
    "primary_role": "Enforcer",
    "network_roles": {
      "NET_BETA": "Enforcer"
    }
  },
  "ENT_013": {
    "name": "Kiaan Bora",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_BETA"
    ],
    "primary_role": "Couriers/Distributor",
    "network_roles": {
      "NET_BETA": "Couriers/Distributor"
    }
  },
  "ENT_014": {
    "name": "Gautami Shere",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_BETA"
    ],
    "primary_role": "Couriers/Distributor",
    "network_roles": {
      "NET_BETA": "Couriers/Distributor"
    }
  },
  "ENT_015": {
    "name": "Nicholas Bhalla",
    "is_criminal": True,
    "is_bridge": True,
    "networks": [
      "NET_BETA",
      "NET_GAMMA"
    ],
    "primary_role": "Cross-Network Bridge Connector",
    "network_roles": {
      "NET_BETA": "Bridge Connector (Identity Supplier)",
      "NET_GAMMA": "Bridge Connector (Data Broker)"
    }
  },
  "ENT_016": {
    "name": "Suhani Loyal",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_GAMMA"
    ],
    "primary_role": "Kingpin / Tech Lead",
    "network_roles": {
      "NET_GAMMA": "Kingpin / Tech Lead"
    }
  },
  "ENT_017": {
    "name": "Hitesh Tata",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_GAMMA"
    ],
    "primary_role": "Phishing Kit Operator",
    "network_roles": {
      "NET_GAMMA": "Phishing Kit Operator"
    }
  },
  "ENT_018": {
    "name": "Kevin Dewan",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_GAMMA"
    ],
    "primary_role": "Call Center Handler",
    "network_roles": {
      "NET_GAMMA": "Call Center Handler"
    }
  },
  "ENT_019": {
    "name": "Tanish Rastogi",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_GAMMA"
    ],
    "primary_role": "SIM Card Extractor",
    "network_roles": {
      "NET_GAMMA": "SIM Card Extractor"
    }
  },
  "ENT_020": {
    "name": "Yashoda Tak",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_GAMMA"
    ],
    "primary_role": "Mule Account Manager",
    "network_roles": {
      "NET_GAMMA": "Mule Account Manager"
    }
  },
  "ENT_021": {
    "name": "Ganga Dutta",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_GAMMA"
    ],
    "primary_role": "Cash Out Mule",
    "network_roles": {
      "NET_GAMMA": "Cash Out Mule"
    }
  },
  "ENT_022": {
    "name": "Sai Sidhu",
    "is_criminal": True,
    "is_bridge": True,
    "networks": [
      "NET_GAMMA",
      "NET_DELTA"
    ],
    "primary_role": "Cross-Network Bridge Connector",
    "network_roles": {
      "NET_GAMMA": "Bridge Connector (Extortion Financier)",
      "NET_DELTA": "Bridge Connector (Financier)"
    }
  },
  "ENT_023": {
    "name": "Deepa Yadav",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_DELTA"
    ],
    "primary_role": "Gang Leader / Arms Supplier",
    "network_roles": {
      "NET_DELTA": "Gang Leader / Arms Supplier"
    }
  },
  "ENT_024": {
    "name": "Manan Saran",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_DELTA"
    ],
    "primary_role": "Extortion Specialist",
    "network_roles": {
      "NET_DELTA": "Extortion Specialist"
    }
  },
  "ENT_025": {
    "name": "Karan Tella",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_DELTA"
    ],
    "primary_role": "Shooter / Enforcer",
    "network_roles": {
      "NET_DELTA": "Shooter / Enforcer"
    }
  },
  "ENT_026": {
    "name": "Manthan Tripathi",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_DELTA"
    ],
    "primary_role": "Arms Courier",
    "network_roles": {
      "NET_DELTA": "Arms Courier"
    }
  },
  "ENT_027": {
    "name": "Ridhi Edwin",
    "is_criminal": True,
    "is_bridge": False,
    "networks": [
      "NET_DELTA"
    ],
    "primary_role": "Hideout Caretaker",
    "network_roles": {
      "NET_DELTA": "Hideout Caretaker"
    }
  }
}

# Civilian entities ENT_028 to ENT_075
for i in range(28, 76):
    eid = f"ENT_{i:03d}"
    ground_truth[eid] = {
        "name": "",  # populated from entities.csv
        "is_criminal": False,
        "is_bridge": False,
        "networks": [],
        "primary_role": "Uninvolved Civilian",
        "network_roles": {}
    }

with open(os.path.join(DATA_DIR, "ground_truth.json"), "w", encoding="utf-8") as f:
    json.dump(ground_truth, f, indent=2)
print("Wrote ground_truth.json")

print("All base data written successfully!")
