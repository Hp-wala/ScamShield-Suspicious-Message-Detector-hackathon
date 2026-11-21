import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)


SCAM = [
("Bank/KYC","sms","en","Your SBI account is at risk of suspension. Open sbi-kyc-update.xyz/login and verify KYC immediately."),
("Bank/KYC","whatsapp","hinglish","Sarkari bank alert: HDFC account aaj block ho sakta hai. OTP aur PAN turant bhejo."),
("Bank/KYC","email","en",'From: "HDFC Bank" <alert@hdfc-secure-login.top>\nReply-To: refund@hdfc-help.xyz\nSubject: KYC blocked\nPlease update PAN and send OTP before midnight.'),
("Bank/KYC","sms","hinglish","ICICI KYC expired dikh raha hai. 0000000000 par OTP call karke confirm karein."),
("Bank/KYC","sms","en","Dear customer, account verification failed. Pay Rs 299 fee at bit.ly/3xYzAb."),
("Bank/KYC","email","hinglish","Axis account freeze notification. KYC link kholkar PIN aur Aadhaar number share karein."),
("Bank/KYC","sms","en","PNB: ATM card suspended. Reply with card number and CVV to restore."),
("Bank/KYC","whatsapp","hinglish","Kotak card band hone wala hai. Is fake link par CVV dalke verify karo: kotak-card-verify.top"),
("Bank/KYC","email","en","UPI ID verification is pending. Scan this QR and enter UPI PIN to receive the refund."),
("Bank/KYC","sms","hinglish","Aapke UPI ka daily limit band. Turbo KYC ke liye hdfc-secure-login.top par jaayein."),
("Bank/KYC","sms","en","Bank security: account frozen for unusual activity. Call 00000-00000 now."),
("Bank/KYC","email","hinglish","SBI reward update. OTP mat bhoolna: reward claim karne ke liye sbi-kyc-update.xyz"),
("Bank/KYC","url","en","hxxp://sbi-kyc-update[.]xyz/account/verify"),
("Bank/KYC","sms","hinglish","RBI notice aaya hai. Aadhaar aur ATM PIN bhejne se KYC activate hoga."),

("Delivery","sms","en","Your India Post parcel is held. Pay 149 processing fee at indiapost-redelivery.click."),
("Delivery","whatsapp","hinglish","DHL jaisa package customs me atka hai. Aapka address aur fee bhejo."),
("Delivery","email","en",'Subject: Amazon package address incomplete\nPay Rs 99 redelivery charge at amaz0n-refund.cfd.'),
("Delivery","sms","hinglish","Delhivery parcel return hua hai. Abhi fee na bhare to lost ho jayega."),
("Delivery","whatsapp","en","Your BlueDart shipment failed twice. Confirm address through bit.ly/3xYzAb."),
("Delivery","sms","en","DTDC: customs clearance pending. Click indiapost-redelivery.click and pay."),
("Delivery","email","hinglish","FedEx package address galat hai. Delivery charge aur card details submit karein."),
("Delivery","sms","en","Parcel 7 hours from dispatch. Small rescheduling fee: amaz0n-refund.cfd."),
("Delivery","whatsapp","hinglish","Amazon COD package ruk gaya. Confirm address aur OTP share karein."),
("Delivery","sms","en","India Post: shipment stuck at border. Pay duty by 23:59."),
("Delivery","email","en","Flipkart order cancelled. Refund will be released after a processing fee."),
("Delivery","sms","hinglish","Aapka courier parcel address ke bina bheja ja raha hai. turant fee transfer karein."),
("Delivery","url","en","http://indiapost-redelivery.click/parcel-update"),
("Delivery","sms","hinglish","BlueDart fee due hai, aaj payment na ho to 00000-00000 par package lost."),

("Government","sms","en","Income Tax refund approved. Pay verification charge at incometax-refund.top."),
("Government","whatsapp","hinglish","Aapka PM Kisan subsidy ruk gaya. Aadhaar link karein."),
("Government","email","en",'From: Income Tax Office <notice@incometax-refund.top>\nSubject: ITR refund\nPay the GST notice fee to claim funds.'),
("Government","sms","hinglish","EPFO refund mila hai. Claim karne ke liye epfo-claim.vip par PAN dalein."),
("Government","sms","en","Your e-challan is unpaid. Fine doubles tonight. Pay at epfo-claim.vip."),
("Government","email","hinglish","DigiLocker KYC pending. Sarkari refund paane ke liye OTP aur Aadhaar bhejein."),
("Government","whatsapp","en","Traffic police: arrest warrant attached. Stay on video call and pay bond."),
("Government","sms","hinglish","UIDAI se Aadhaar suspension notice. Aaj hi data verify karein."),
("Government","email","en","GST audit penalty due immediately. Open incometax-refund.top/payment."),
("Government","sms","en","Court summons: a narcotics parcel is linked to you. Do not contact police."),
("Government","whatsapp","hinglish","CBI NCB digital arrest: video call par rahein aur transfer fee na batayein."),
("Government","sms","en","PM Kisan: beneficiary status blocked. SMS your Aadhaar and bank OTP."),
("Government","url","en","hxxp://uidai-verification[.]top/kyc"),
("Government","email","hinglish","IRCTC refund pending hai. Railway service charge pehle pay karein."),

("Lottery/Prize","sms","en","Congratulations, you won a car in a lucky draw. Send a 499 claim fee."),
("Lottery/Prize","whatsapp","hinglish","Aapne crore ka inaam jeeta hai. Processing charge bhejkar reward lein."),
("Lottery/Prize","email","en","Claim Department: Your prize is awaiting customs clearance. Pay first."),
("Lottery/Prize","sms","hinglish","Bonus cashback 25 lakh. Turant lucky link par OTP verify karein."),
("Lottery/Prize","whatsapp","en","You are the millionth customer. Share bank PIN to unlock gift."),
("Lottery/Prize","sms","en","Amazon lucky reward: Rs 50,000 credited. Pay tax at amaz0n-refund.cfd."),
("Lottery/Prize","email","hinglish","Lottery winner certificate attached. Claim fee aur Aadhaar number chahiye."),
("Lottery/Prize","sms","en","Final chance: select one gift and pay registration."),
("Lottery/Prize","whatsapp","hinglish","Kismat khuli: aapko <fake> prize mila. Advance tax bhejiye."),
("Lottery/Prize","sms","en","Cashback jackpot for 0000000000. Tap bit.ly/3xYzAb."),
("Lottery/Prize","email","en","You have won 2 crore rupees. The claim desk needs a refundable fee."),
("Lottery/Prize","sms","hinglish","Jeet ka certificate mila. Claim reward ke liye CVV bhejo."),
("Lottery/Prize","url","en","http://prize-claim.xyz/reward"),
("Lottery/Prize","whatsapp","hinglish","Lucky draw se inaam mila. 00000-00000 par call karein."),

("Job/Work-from-home","whatsapp","en","Work from home for 5000 rupees daily. Pay registration then start."),
("Job/Work-from-home","sms","hinglish","Ghar baithe likes aur tasks karo, roj 3000 kamao. Telegram join karein."),
("Job/Work-from-home","whatsapp","en","Telegram job: no experience. First buy a gift card for training."),
("Job/Work-from-home","email","hinglish","Remote part-time offer. Salary 50000, security deposit pehle bhejo."),
("Job/Work-from-home","sms","en","Earn 2000 by rating hotels. Advance fee unlocks account."),
("Job/Work-from-home","whatsapp","hinglish","Video like karke daily earning. Telegram par team se payment setup."),
("Job/Work-from-home","email","en","Hiring now. Training requires a refundable APK download."),
("Job/Work-from-home","sms","hinglish","Ad review job me har task ke liye deposit badhta hai. Abhi pay karein."),
("Job/Work-from-home","whatsapp","en","HR: WhatsApp interview now. Pay for offer letter."),
("Job/Work-from-home","sms","en","Simple task work pays 1500/day. Join bit.ly/3xYzAb."),
("Job/Work-from-home","email","hinglish","Telegram se hiring. Aadhaar, OTP aur processing fee mangi ja rahi hai."),
("Job/Work-from-home","whatsapp","en","Customer service role for 1000/day. Deposit for software."),
("Job/Work-from-home","url","en","hxxp://daily-task-job[.]top/register"),
("Job/Work-from-home","sms","hinglish","Ghar baithe 20 minute kaam aur daily cash. 00000-00000 par HR se baat karein."),

("UPI/Payment","sms","en","UPI collect request for 5000. Accept it to receive the mistaken payment."),
("UPI/Payment","whatsapp","hinglish","QR scan karo lekin paisa receive karne ke liye OTP aur PIN mat batana."),
("UPI/Payment","sms","en","Wrong transfer by mistake. Return via UPI PIN at 0000000000."),
("UPI/Payment","email","hinglish","Refund mil raha hai. Collect request accept karke PIN verify karein."),
("UPI/Payment","whatsapp","en","Scan QR to receive prize. Never mind, UPI PIN is needed."),
("UPI/Payment","sms","hinglish","Mera payment sent by mistake. Turant collect request accept karo."),
("UPI/Payment","whatsapp","en","Do not receive; just accept and enter PIN for cashback."),
("UPI/Payment","sms","en","Your cashback is waiting. Accept collect request in UPI app."),
("UPI/Payment","email","hinglish","Wrong transfer complaint. Paisa wapas karne ke liye QR scan karein."),
("UPI/Payment","sms","en","Merchant refund stuck. Approve request, then enter UPI PIN."),
("UPI/Payment","whatsapp","hinglish","Double cashback offer. Sirf scan QR and PIN confirm."),
("UPI/Payment","sms","en","Collect request: 1 rupee. Complete by entering OTP."),
("UPI/Payment","url","en","hxxp://upi-refund[.]top/collect"),
("UPI/Payment","whatsapp","hinglish","Galti se 8000 bheje. 00000-00000 par PIN aur OTP bhejo."),

("Electricity/Utility","sms","en","Electricity bill unpaid. Meter disconnect at 9 PM tonight."),
("Electricity/Utility","whatsapp","hinglish","Bijli bill pending hai. Aaj raat 9:30 connection kat jayega."),
("Electricity/Utility","email","en","Immediate electricity disconnection notice. Pay officer via bit.ly/3xYzAb."),
("Electricity/Utility","sms","hinglish","Bijli ka final notice. Payment na hua to 00000-00000 par fine lagega."),
("Electricity/Utility","sms","en","Gas cylinder subsidy is blocked. Send card PIN to restore."),
("Electricity/Utility","whatsapp","hinglish","Paani bill overdue. Aaj shaam supply band, officer ko fee bhejo."),
("Electricity/Utility","email","en","Broadband disconnection in 2 hours. Download invoice and pay."),
("Electricity/Utility","sms","hinglish","Meter verification pending. Aaj raat se light kat jayegi."),
("Electricity/Utility","sms","en","Water connection: unpaid bill. Pay via unofficial payment link."),
("Electricity/Utility","whatsapp","hinglish","Utility bill refund mila hai. Bank OTP dekar claim karein."),
("Electricity/Utility","email","en","Final disconnection warning. Your electricity officer will call."),
("Electricity/Utility","sms","hinglish","Bijli office se urgent message. 00000-00000 par turant call."),
("Electricity/Utility","url","en","http://bijli-bill-pending.xyz/pay"),
("Electricity/Utility","email","hinglish","Gas subsidy suspended. 4 digit PIN aur Aadhaar bhejein."),

("Investment","whatsapp","en","Guaranteed 3 percent daily returns. Join VIP crypto group."),
("Investment","email","hinglish","Stock tips VIP. Double paise aur crypto profit ke liye deposit."),
("Investment","sms","en","Invest 1000 today and receive 100000 tomorrow."),
("Investment","whatsapp","hinglish","Naye scheme me double money. Telegram VIP link join karein."),
("Investment","email","en","Secret trading bot. Send funds to unlock guaranteed returns."),
("Investment","sms","hinglish","Market tips for sure profit. 00000-00000 par membership fee."),
("Investment","whatsapp","en","Crypto expert group: 5x profit. Pay for withdrawal."),
("Investment","email","hinglish","SBI investor reward. High return ke liye OTP aur investment transfer."),
("Investment","sms","en","Ponzi-style VIP fund: use 1 rupee and earn 100."),
("Investment","whatsapp","hinglish","Gold investment guaranteed. Registration fee turant bhejo."),
("Investment","email","en","An advisor claims no risk. Send advance fee for portfolio."),
("Investment","sms","hinglish","Daily 2 percent stock tip. Telegram join aur amount bhejein."),
("Investment","url","en","hxxp://vip-investment[.]top/profit"),
("Investment","whatsapp","hinglish","Crypto withdrawal blocked. Tax deposit bina real app ke mat karein."),

("Impersonation","sms","en","Hi Mum, this is my new number. Please send me money urgently."),
("Impersonation","whatsapp","hinglish","Maine phone kho diya. Mujhe Rs 2823 bhejo."),
("Impersonation","sms","en","Hi Papa, lost phone. Buy gift cards and send codes."),
("Impersonation","whatsapp","hinglish","Didi ka naya number hai. UPI se 500 bhej do."),
("Impersonation","email","en","From your son: new email, need emergency cash."),
("Impersonation","sms","hinglish","Boss bol raha hoon. Salary advance 00000-00000 par bhejo."),
("Impersonation","whatsapp","en","New number, don't call the old one. Send a private reply."),
("Impersonation","sms","en","I am stranded. Pay hotel at 0000000000."),
("Impersonation","whatsapp","hinglish","Mera phone lost hai. HDFC PIN mat poochna but cash bhejo."),
("Impersonation","email","en","CEO request: purchase vouchers and share codes."),
("Impersonation","sms","hinglish","Bhai ka naya number. Emergency me Rs 3000 bhej do."),
("Impersonation","whatsapp","en","A relative is requesting gift cards instead of a call."),
("Impersonation","sms","en","Your doctor: pay consultation fee to 0000000000."),
("Impersonation","email","hinglish","Office manager ka message. Salary advance abhi bhejein."),

("Digital Arrest","whatsapp","en","Digital arrest warrant. Stay on video call and do not tell anyone."),
("Digital Arrest","sms","hinglish","CBI ne digital arrest notice bheja. Turant Skype video par raho."),
("Digital Arrest","email","en","NCB seizure notice. Narcotics parcel found. Pay investigation bond."),
("Digital Arrest","whatsapp","hinglish","Police se CBI number par call. Koi ko mat batana, paisa transfer karo."),
("Digital Arrest","sms","en","Money laundering case. Remain on WhatsApp video until clearance."),
("Digital Arrest","email","hinglish","Arrest warrant PDF: signature aur bank OTP ke bina release nahi."),
("Digital Arrest","whatsapp","en","Virtual arrest: show Aadhaar and move money to safety account."),
("Digital Arrest","sms","hinglish","CBI officer bol rahe hain. 00000-00000 par security fee bhejo."),
("Digital Arrest","email","en","ED inquiry. Turn off phone and send crypto bond."),
("Digital Arrest","whatsapp","hinglish","National crime bureau case hai. Family ko mat batana."),
("Digital Arrest","sms","en","Supreme Court case: 30-minute video verification or arrest."),
("Digital Arrest","email","hinglish","Narcotics parcel aapke naam pe mila. Bail fee aur OTP chahiye."),
("Digital Arrest","url","en","hxxp://digital-arrest-cbi[.]top/case"),
("Digital Arrest","whatsapp","hinglish","Police call par video bandh mat karo. Safety account me paise bhejo."),

("Other","sms","en","Install AnyDesk APK and share screen code for account verification."),
("Other","whatsapp","hinglish","QuickSupport app download karo, OTP screen par dikhao."),
("Other","email","en","Download attached setup.exe to receive your refund."),
("Other","sms","hinglish","TeamViewer install karke support ID 00000 bhejo."),
("Other","whatsapp","en","Forward this message many times to activate cashback."),
("Other","email","hinglish","Jo link open karega uska SIM reward milega. APK attach hai."),
("Other","sms","en","Verify your SIM KYC by calling 0000000000."),
("Other","whatsapp","hinglish","New mobile number par 5000 reward. UPI PIN nahi chahiye."),
("Other","email","en","Response required: remote access to protect your bank account."),
("Other","sms","hinglish","Gift card code bhejo aur 2 crore inaam claim karo."),
("Other","whatsapp","en","Join forwarded chain for free recharge."),
("Other","email","hinglish","Refund office se link: secure OTP aur device access."),
("Other","url","en","hxxp://cashback-apk[.]top/update.apk"),
("Other","sms","hinglish","WhatsApp group join karke recharge prize paao."),
]


GENUINE = [
("sms","en","Do not share this OTP. Your bank never asks for it."),
("sms","en","The OTP for your login expires in five minutes. Enter it only inside the official app."),
("sms","en","Rs 499 debited from account <fake>. Available balance Rs 5600."),
("sms","hinglish","Bank se Rs 499 debited hua. OTP koi bhi maangta hai to mat dena."),
("sms","en","Credit of Rs 1250 received. No action or PIN is required."),
("sms","hinglish","Aapka account credit hua. KYC already verified hai, koi action nahi."),
("sms","en","Your debit card KYC is complete. We will never call for your PIN."),
("sms","en","UPI payment was successful. Entering PIN is only for sending money."),
("sms","hinglish","UPI payment successful. Paisa receive karne ke liye PIN nahi chahiye."),
("sms","en","Security alert: your password was changed. Review it in the official app."),
("whatsapp","hinglish","Kal lunch chala? Main 1 baje aaunga."),
("sms","en","Your electricity bill is due on 30 June. Pay through the official utility app."),
("sms","hinglish","Bijli bill Rs 1200 ka hai. Dues printed date tak dena."),
("sms","en","Gas booking confirmed. Please keep the OTP private."),
("sms","hinglish","LPG delivery kal subah. Cash ya UPI se payment available."),
("sms","en","Water bill notice is ready. No payment link or fee is included."),
("sms","en","Broadband plan renews tomorrow. Review the official invoice."),
("sms","hinglish","Internet recharge 28 din ke liye hua. Customer care ko PIN mat batayein."),
("whatsapp","en","The appointment is at 10:30 am. Please arrive ten minutes early."),
("sms","en","Doctor appointment confirmed for Monday. Reply only to reschedule."),
("sms","hinglish","Class tomorrow 8 baje hai. Meeting link calendar me hai."),
("whatsapp","hinglish","Flight ticket mila, official airline app se seat check karo."),
("sms","en","Train PNR update available. No fee or OTP is required."),
("sms","hinglish","Aaj bus late hai. Driver se official helpline par baat hui."),
("sms","en","Your Amazon order was shipped. Track it on https://www.amazon.in."),
("sms","hinglish","Flipkart parcel dispatched hai. Official app flipkart.com se track karein."),
("email","en","Order delivered by BlueDart. No redelivery fee is due."),
("email","hinglish","India Post parcel deliver hua. https://www.indiapost.gov.in par status dekhein."),
("sms","en","Delhivery package delivery updated. The courier will not ask for OTP."),
("sms","hinglish","Courier address confirm karna hai? Sirf official app me update karein."),
("sms","en","Parcel fees are included in the order total. No extra payment is needed."),
("email","en","Income tax acknowledgement is available at https://www.incometax.gov.in."),
("sms","en","Your PAN and Aadhaar KYC is already verified. No action needed."),
("sms","hinglish","e-Challan ka status official portal par check karein. Payment short link mat kholna."),
("sms","en","PM Kisan status is available only at pmkisan.gov.in."),
("email","hinglish","EPFO statement taiyar hai. Official portal epfindia.gov.in se download karein."),
("sms","en","UIDAI appointment confirmed. You will not be asked to pay a fee."),
("sms","hinglish","DigiLocker document safe hai. OTP kisi se share mat karein."),
("sms","en","IRCTC booking confirmed. No penalty or urgent transfer is needed."),
("email","en","School fee reminder: pay only through the school portal."),
("whatsapp","hinglish","Fees ekdum normal hai; reminder dekhkar school app se pay karna."),
("sms","en","Exam registration date is confirmed. The portal does not accept gift cards."),
("sms","hinglish","Library book due kal hai. Fee official desk par lagegi."),
("whatsapp","en","Movie tickets are confirmed. Entry is by QR at the venue."),
("sms","en","Mobile recharge successful for 28 days. No PIN was sent."),
("sms","hinglish","Jio plan recharge ho gaya. Koi OTP verify nahi karna."),
("whatsapp","en","Airtel data plan renews after the date shown in the app."),
("sms","en","Bank statement is ready for download in internet banking."),
("sms","hinglish","Credit card statement aa gayi. PIN ya CVV link par mat dalein."),
("email","en","Your account statement is enclosed. It does not request payment."),
("whatsapp","hinglish","Lunch tomorrow? 1 baje office ke paas milte hain."),
("whatsapp","en","Are we still meeting at the coffee shop? Reply when free."),
("sms","hinglish","Class cancel ho gayi, next week ka schedule mil jayega."),
("sms","en","Your petrol cashback was posted as a reward. It requires no claim fee."),
("email","hinglish","Cashback already account me credit hua. Koi prize link mat kholna."),
("sms","en","Insurance premium receipt generated. Verify through the insurer app."),
("sms","hinglish","Policy reminder hai, payment official website par hi karein."),
("whatsapp","en","Happy birthday! Hope you have a relaxed day."),
("sms","en","Family group: dinner at 7 pm. Please confirm attendance."),
("whatsapp","hinglish","Shaadi ka card mil gaya. 14 tareekh ko milenge."),
("sms","en","Gym session starts at 6 pm. Bring the booking confirmation."),
("sms","hinglish","Car service ho gaya. Bill garage receipt me attached hai."),
("whatsapp","en","The repair is complete. Pick up tomorrow using the receipt."),
("sms","en","Library card renewal approved. No online fee is due."),
("sms","hinglish","Post office passbook update ho gaya. Branch me collect karein."),
("email","en","Government pension statement available at https://www.epfindia.gov.in."),
("sms","en","Your Voter ID appointment is confirmed for Wednesday."),
("sms","hinglish","Aadhaar card update already done. No urgent action."),
("sms","en","DigiLocker shares a notice that no OTP or PIN is ever required."),
("email","hinglish","Sarkari scholarship status approved hai. Official portal par dekhein."),
("sms","en","Scholarship disbursement is expected after document verification."),
("whatsapp","hinglish","Birthday gift Amazon se aaya, official tracking link me status hai."),
("sms","en","Your order is shipped from the official store. No customs fee."),
("sms","hinglish","Parcel aaj delivered hua. Delivery boy ko OTP mat batana."),
("sms","en","Food order delivered. Please rate the service in the app."),
("whatsapp","hinglish","Dinner aa gaya aur khana accha tha."),
("sms","en","Flight check-in opens at 10 am. Use only the airline app."),
("sms","hinglish","Metro card recharge successful. Gate par PIN nahi dena."),
("sms","en","Bus seat is confirmed. Ticket is stored in the official app."),
("sms","en","Hotel booking confirmed for two nights. No advance payment now."),
("whatsapp","hinglish","Hotel 3 pm check-in karega. Booking detail calendar me hai."),
("sms","en","Parking payment is complete. Keep the receipt."),
("sms","hinglish","Toll recharge hua. FASTag alert sirf official account se aaega."),
("sms","en","Your KYC review is complete. No further documents are needed."),
("sms","hinglish","Bank ne urgent KYC verification ka message bheja? Ignore: KYC already verified."),
("sms","en","A genuine OTP was sent for sign-in. Never share it with anyone."),
("email","en","This prize notification is a family reminder, not a cash claim."),
("sms","hinglish","Prize koi nahi mila hai. Koi fee ya reward link mat kholna."),
("sms","en","A suspicious parcel text arrived. We checked: no package is held."),
("sms","hinglish","Electricity bill message fake laga. Official app se status verify hua."),
("whatsapp","en","Friend: I sent a wrong-looking refund link. Please do not open it."),
("sms","hinglish","UPI collect request aayi thi. Maine reject karke PIN share nahi kiya."),
("email","en","This bank notice contains urgent words, but it is only a document reminder."),
("sms","en","Refund is already in your account. No bank OTP is needed."),
("sms","hinglish","Income tax refund update genuine hai aur koi fee nahi."),
("sms","en","This fee notice is from school, not a courier or bank."),
("sms","hinglish","OTP aur KYC update ki warning: official app se verify."),
("whatsapp","en","The parcel address is correct. Delivery updates come from the store."),
("sms","en","No phone call or link is needed to receive this recharge."),
("sms","hinglish","Telegram ka job message suspicious tha, isliye apply nahi kiya."),
("sms","en","You are not under arrest. This is a family reminder to attend court only if summoned."),
("email","hinglish","Investment se koi guaranteed profit nahi hua. Update official account me hai."),
("sms","en","A normal bank transfer was completed. Customer support never asks for OTP."),
("sms","hinglish","UPI se paisa aaya, lekin collect request ya QR se kuch nahi hona."),
("sms","en","The card will not be blocked. The bank link asks for no PIN."),
("email","en","Normal credit card statement: no prize, fee or urgent action."),
("sms","hinglish","Parcel delivered; ek extra fee maangne wala link fake hai."),
("whatsapp","en","Can you call me after lunch? This is my regular number."),
("sms","en","Appointment reminder: 4 pm at the clinic. No deposit is required."),
("sms","hinglish","Vaccination slot confirm hai, koi KYC OTP nahi chahiye."),
("email","en","Bank statement is attached. The sender does not request remote access."),
("sms","en","Your subscription renews at the listed price. No gift card needed."),
("sms","hinglish","Recharge plan valid hai. 0-day expiry ka koi urgent message nahi."),
("whatsapp","en","Normal school chat: bring the notebook and water bottle."),
("sms","en","Salary credited. The monthly payslip is in the employee portal."),
("sms","hinglish","Salary account me aa gayi. Bank ko CVV bhejne ki zarurat nahi."),
("email","en","Meeting invitation: discuss quarterly reports on Tuesday."),
("sms","en","No claim or prize: this is a scheduled medication reminder."),
("whatsapp","hinglish","Medicine 8 baje leni hai. Reminder save kar liya."),
("sms","en","Insurance claim status is processing. No fee or OTP is due."),
("email","hinglish","Utility bill normal hai. Official meter number se verify kiya."),
("sms","en","Customer survey received. No account details are required."),
("sms","hinglish","Bank account me cashback credit hua. Fake prize link ignore karein."),
("whatsapp","en","Your friend says the parcel is at home. Confirm when convenient."),
("sms","en","The parking reservation is confirmed. No extra customs or duty fee."),
("email","hinglish","Office lunch order confirm hai. Address official app me sahi hai."),
("sms","en","The electricity meter reading was submitted successfully."),
("sms","hinglish","Bijli meter photo upload hua. Bill later official app me milega."),
("whatsapp","en","The real school portal sent a fee reminder. It never asks for OTP."),
("email","en","Calendar invitation: team stand-up at 9 am."),
("sms","hinglish","Aaj ka office meeting cancel hua. Naya time kal milega."),
("sms","en","Bank OTP warning: never share the code, even if the caller sounds urgent."),
("whatsapp","hinglish","Papa se baat hui. Sirf regular number se call aaega."),
("sms","en","Your KYC status is already verified. The bank asked for no documents today."),
("whatsapp","hinglish","OTP kal ke sign-in ke liye tha. Koi OTP abhi share mat karo."),
("sms","en","Debit card is active. No fee is required to unblock it."),
("email","hinglish","Delivery reminder normal hai. Parcel ka extra customs fee nahi hai."),
("sms","en","Prize message was checked. There is no cash reward or claim fee."),
("whatsapp","hinglish","Bijli ka bill time se pay ho jayega. Link official app ka hai."),
("sms","en","Refund credited to the account. No UPI PIN or QR action is needed."),
("email","hinglish","Income tax notice ka status dekha. No penalty or payment link."),
("sms","en","A genuine school fee notice arrived. It does not request gift cards."),
("whatsapp","hinglish","Telegram job offer fake laga. Maine apply ya deposit nahi kiya."),
("sms","en","The court summons is official only through the published government portal."),
("email","hinglish","Investment update regular hai. Guaranteed profit ka koi claim nahi."),
("sms","en","Courier called for a real address check. No OTP was requested."),
("whatsapp","hinglish","UPI collect request reject kiya. PAN ya PIN nahi bheja."),
("sms","en","Cashback was posted by the card app; no prize claim is pending."),
("email","hinglish","Sarkari Aadhaar update ka reminder normal hai. Koi remote app required nahi."),
("sms","en","Normal bank statement is ready. Support will never call to collect the OTP."),
]


def normalise_key(text):
    text = str(text).lower()
    text = re.sub(r"\b\d+(?:[.,]\d+)*\b", "#", text)
    text = re.sub(r"[^a-z0-9#]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def dedupe(rows):
    seen = set()
    result = []
    for row in rows:
        key = normalise_key(row["text"])
        if key in seen:
            continue
        seen.add(key)
        result.append(row)
    return result


def write_dataset():
    scam_rows = []
    link_suffixes = [
        " Open fake URL sbi-kyc-update.xyz/check.",
        " Call fake support 0000000000.",
        " Use hxxp://amaz0n-india[.]top/claim.",
        " Visit hdfc-secure-login.top/verify.",
        " Tap indiapost-redelivery.click/status.",
        " Try epfo-claim.vip/refund.",
    ]
    for category, channel, lang, text in SCAM:
        row = {"text": text, "label": "scam", "category": category, "channel": channel, "lang": lang}
        if not re.search(r"https?://|hxxp://|bit\.ly|0000|[-.]xyz|[-.]top|[-.]click|[-.]cfd|[-.]vip", text, re.I):
            suffix = link_suffixes[len(scam_rows) % len(link_suffixes)]
            row["text"] = text + suffix
        scam_rows.append(row)
    genuine_rows = []
    for channel, lang, text in GENUINE:
        genuine_rows.append({"text": text, "label": "genuine", "category": "", "channel": channel, "lang": lang})
    scam_rows = dedupe(scam_rows)
    genuine_rows = dedupe(genuine_rows)
    if len(scam_rows) < 150 or len(genuine_rows) < 150:
        raise SystemExit(f"Need at least 150 rows per label, got scam={len(scam_rows)} genuine={len(genuine_rows)}")
    rows = scam_rows[:150] + genuine_rows[:150]
    if len(rows) < 300:
        raise SystemExit(f"Expected at least 300 unique rows, got {len(rows)}")
    if len(rows) > 300:
        rows = rows[:300]
    DATA.mkdir(exist_ok=True)
    path = DATA / "dataset.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["text", "label", "category", "channel", "lang"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"dataset_rows={len(rows)} scam={sum(r['label']=='scam' for r in rows)} genuine={sum(r['label']=='genuine' for r in rows)}")
    print(f"size={path.stat().st_size} bytes")


if __name__ == "__main__":
    write_dataset()
