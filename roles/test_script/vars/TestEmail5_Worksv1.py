import win32com.client
olMailItem = 0x0
obj = win32com.client.Dispatch("Outlook.Application")
newMail = obj.CreateItem(olMailItem)
newMail.Subject = "changes pending Q&C approval for closure"
newMail.Body = """Hi Regional Directors,

Attached is the list of changes pending Q&C approval for closure. 
If you have concerns about the delay, please escalate to Aisha Davies (ADavies7@its.jnj.com).

Thanks, 
Gina 
"""
newMail.To = "gpierre@its.jnj.com"
attachment1 = "C:\Data\Changes Pending Q&C Approvals by Region.xlsx"
newMail.Attachments.Add(attachment1)
newMail.Send()
