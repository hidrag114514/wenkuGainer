from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
import base64
import time
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A3


class GetImgFromCanvas:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Chrome()
        self.pagenum = 1
        self.elementName = "page_%d" % self.pagenum
        self.continueButton = "continueButton"
        self.flag = 1
        self.sleepTime = 7
        if not os.path.exists("images"):
            os.makedirs("images")

    def elementToImage(self):
        print("page %d" % self.pagenum)
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, self.elementName))
        )
        canvas_base64 = self.driver.execute_script(
            "return arguments[0].toDataURL('image/png').substring(21);", element
        )
        with open("images/canvas_image%d.png" % (self.pagenum), "wb") as file:
            file.write(base64.b64decode(canvas_base64))

        elementHeight = element.size["height"]
        return elementHeight

    def run(self, page):
        self.driver.get(self.url)
        time.sleep(self.sleepTime)
        while self.pagenum <= page:
            if self.pagenum <= 5:
                eH = self.elementToImage()

            if self.pagenum > 5:
                if self.flag == 1:
                    continueButtonElement = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, self.continueButton))
                    )
                    self.flag = 0
                    action = ActionChains(self.driver)
                    action.move_to_element(continueButtonElement).click().perform()

                    time.sleep(self.sleepTime)

                eH = self.elementToImage()

            self.pagenum += 1
            self.elementName = "page_%d" % self.pagenum
            # 向下滚动画布尺寸的高度
            self.driver.execute_script("window.scrollBy(0, %d);" % eH)
            time.sleep(2)

        self.driver.quit()

    def savePdf(self, filename, pages):
        # 定义PDF页面大小（以像素为单位）
        page_width, page_height = A3
        # 创建一个pdf对象
        c = canvas.Canvas("%s.pdf" % filename, pagesize=(page_width, page_height))
        # 读取图片
        for i in range(1, pages + 1):
            img = Image.open("images/canvas_image%d.png" % i)
            # 计算缩放比例
            width_ratio = page_width / img.width
            height_ratio = page_height / img.height
            ratio = min(width_ratio, height_ratio)

            # 调整图像大小
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            img = img.resize((new_width, new_height))
            # 将图片添加到pdf文件中
            c.drawInlineImage(img, 0, 0, width=new_width, height=new_height)
            # 保存pdf文件
            c.showPage()
        c.save()


# test = GetImgFromCanvas("https://www.doc88.com/p-40159595459205.html")
# # test.run(14)
# test.savePdf("output", 17)


if __name__ == "__main__":
    url = input("请输入啥比道格网站的url:")
    pages = int(input("请输入要保存的页数:"))
    filename = input("请输入要保存的pdf文件名:")
    test = GetImgFromCanvas(url)
    test.run(pages)
    test.savePdf(filename, pages)
