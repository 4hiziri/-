"平成26年度版"
import ConfigParser
import requests
from bs4 import BeautifulSoup


# 科目毎にほぼ同じなので科目毎にクラスにしてやる
# ひとつだけ卒業研究が入るので、継承する


class Subject:
    unit = 0
    border = 0
    representation = ""

    def __init__(self, unit, border, string):
        self.unit = unit
        self.border = border
        self.representation = string

    def __str__(self):
        return self.representation

    def check(self):
        "足りない分を計算する"
        return max(self.unit - self.border, 0)


class Special_Subject:
    "専門系科目"
    special_basic_subject = 0
    sbs_str = '専門基礎科目'
    special_subject = 0
    ss_str = '専門科目'
    special_related_subject = 0
    srs_str = '関連専門科目'

    def __init__(self, summary_dict):
        self.special_basic_subject = summary_dict[self.sbs_str]
        self.special_subject = summary_dict[self.ss_str]
        self.special_related_subject = summary_dict[self.srs_str]

    def check(self):
        insufficient_subject = []

        def append_if_lt(subject_score, needed_score, subject_str):
            if subject_score < needed_score:
                insufficient_subject.append((subject_str,
                                             needed_score - subject_score))

        append_if_lt(self.special_basic_subject, 44, self.sbs_str)
        append_if_lt(self.special_subject, 31, self.ss_str)
        append_if_lt(self.special_related_subject, 6, self.srs_str)

        return insufficient_subject


class Educational_Subject:
    "全学教育科目"

    basic_subject = 0  # 全学基礎科目の単位
    bunkei_subject = 0  # 文系科目の単位、英語での表現がいいのない
    science_basic_subject = 0  # 理系基礎科目
    science_cultural_subject = 0  # 理系教養科目
    zengaku_cultural_subject = 0  # 全学教養科目+開放科目

    def __init__(self, summary_dict):
        self.basic_subject = summary_dict['基礎セミナー'] + summary_dict['言語文化'] + \
            summary_dict['健康・スポーツ科学（実習）'] + summary_dict['健康・スポーツ科学（講義）']
        self.bunkei_subject = summary_dict['文系基礎科目'] + summary_dict['文系教養科目']
        self.science_basic_subject = summary_dict['理系基礎科目']
        self.science_cultural_subject = summary_dict['理系教養科目']
        self.zengaku_cultural_subject = summary_dict['開放科目'] + \
            summary_dict['全学教養科目']

    def check(self):
        insufficient_subject = []

        def append_if_lt(subject_score, needed_score, subject_str):
            if subject_score < needed_score:
                insufficient_subject.append((subject_str,
                                             needed_score - subject_score))

        append_if_lt(self.basic_subject, 16, "全学基礎科目")
        append_if_lt(self.bunkei_subject, 4, "文系科目")
        append_if_lt(self.science_basic_subject, 23, "理系基礎科目")
        append_if_lt(self.science_cultural_subject, 4, "理系教養科目")
        append_if_lt(self.zengaku_cultural_subject, 2, "全学教養科目")

        sum = self.basic_subject + self.bunkei_subject + self.science_basic_subject + \
            self.science_cultural_subject + self.zengaku_cultural_subject
        append_if_lt(sum, 55, "合計")

        return insufficient_subject


# HACK: dirty work
class Subject:
    special_subject = None
    educational_subject = None

    def __init__(self, summary_dict):
        self.special_subject = Special_Subject(summary_dict)
        self.educational_subject = Educational_Subject(summary_dict)

    def check(self):
        return self.special_subject.check() + self.educational_subject.check()


def table_dict(bs_table):
    td_list = map(lambda tr: tr.find_all('td'), bs_table.find_all('tr'))
    return dict(
        map(lambda tds: (tds[0].text.strip()[1:], float(tds[1].text.strip())),
            td_list))


# table[1]
def extract_subjects(bs_table):
    def to_string(elem):
        if elem.find('th') is not None:
            text = elem.find('th').text
        elif elem.find('td') is not None:
            text = elem.find('td').text
        else:
            raise Exception("Not th or td")

        return text.replace(' ', '').replace('【', '[').replace('】', ']')

    return list(map(lambda x: to_string(x), bs_table.find_all('tr')))[1:]


def subjects_to_dict(subjects):
    dict = {}
    tmp_list = []
    subject_sort = ""

    for sub in subjects:
        if sub[0] == '[':
            dict[subject_sort] = tmp_list
            tmp_list = []
            subject_sort = sub[1:-1]
        else:
            tmp_list.append(sub)

    del(dict[''])
    return dict


def get_summary_score(url):
    bs = BeautifulSoup(requests.get(url).text, "html.parser")
    return Subject(table_dict(bs.find_all('table')[2]))


def parse_syllabus(url):
    bs = BeautifulSoup(requests.get(url).text, "html.parser")
    


def main(url):
    conf = ConfigParser.SafeConfigParser()
    conf.read('setting.conf')

    print("足りない分")

    for subject, score in get_summary_score(url).check():
        print(subject + ": " + str(score))

    return


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("履修ページのURL")
        exit()

    main(sys.argv[1])
