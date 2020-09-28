sentence_list = []


def get_word_tag_list(sentence):
    ret = []
    word_tag_list = sentence.strip().split()[1:]

    for word_tag in word_tag_list:
        if word_tag.startswith('['):
            word_tag = word_tag[1:]
        elif ']' in word_tag:
            word_tag = word_tag[:word_tag.index(']')]

        ret.append(word_tag)
    return ret


def load_sentence_list():
    with open('1998-01-105-带音.txt', "r", encoding='gbk') as f:
        for line in f:

            get_word_tag_list(line)

            word_tag_list = get_word_tag_list(line)
            if len(word_tag_list) == 0:
                continue
            word_list = [word_tag.split('/')[0] for word_tag in word_tag_list]
            sentence_list.append(word_list)


observation_status_list = []
test_observation_status_list = []


def output_result(observation, status):
    list = ""
    for i, status in enumerate(status):
        if (i >= len(observation)):
            break

        list += observation[i]
        if (status == 'e'):
            list += "/ "
        elif status == 's':
            list += "/ "

    print(list)





def load_observation_status_list():
    for idx, sentence in enumerate(sentence_list):
        observation = ""
        status = ""
        for word in sentence:
            if (len(word) == 1):
                status += 's'
            elif (len(word) == 2):
                status += 'be'
            else:
                status += 'b'
                for i in range(len(word) - 2):
                    status += 'i'
                status += 'e'
            observation += word

        if idx % 10 < 8:
            observation_status_list.append((observation, status))
        else:
            test_observation_status_list.append((observation, status))


status_list = ['b', 'i', 'e', 's']

a_fenmu = {}

for status in status_list:
    a_fenmu[status] = 0
a_fenmu['0'] = 0

a_fenzi = {}
for status_i in status_list:
    for status_j in status_list:
        a_fenzi[(status_i, status_j)] = 0

    a_fenzi[('0', status_i)] = 0
    a_fenzi[(status_i, 'f')] = 0


def static_a():
    for observation, status in observation_status_list:
        for i in range(1, len(status)):
            a_fenmu[status[i - 1]] += 1
            a_fenzi[(status[i - 1], status[i])] += 1

        a_fenmu['0'] += 1
        a_fenzi[('0', status[0])] += 1

        a_fenmu[status[-1]] += 1
        a_fenzi[(status[-1], 'f')] += 1


a = {}


def compute_a():
    for status_i in status_list:
        for status_j in status_list:
            a[(status_i, status_j)] = a_fenzi[(status_i, status_j)] / a_fenmu[status_i]

        a[('0', status_i)] = a_fenzi[('0', status_i)] / a_fenmu['0']

        a[(status_i, 'f')] = a_fenzi[(status_i, 'f')] / a_fenmu[status_i]


b_fenmu = {}
b_fenzi = {}


def static_b():
    for observation, status in observation_status_list:
        for i in range(len(status)):
            q = status[i]
            o = observation[i]
            if q not in b_fenmu:
                b_fenmu[q] = 0
            b_fenmu[q] += 1
            if (q, o) not in b_fenzi:
                b_fenzi[(q, o)] = 0
            b_fenzi[(q, o)] += 1


b = {}


def compute_b():
    for (q, o) in b_fenzi:
        b[(q, o)] = b_fenzi[(q, o)] / b_fenmu[q]


def segment(sentence):
    alpha = {}  # 二维数组  结尾加一个ajf
    for i in range(len(sentence)):
        for status in status_list:
            if (i == 0):
                if (status, sentence[0]) in b:
                    launch_probability = b[(status, sentence[0])]
                else:
                    launch_probability = 1e-10
                alpha[(i, status)] = a[('0', status)] * launch_probability
            else:
                alpha[(i, status)] = 0
    alpha[(len(sentence), 'f')] = 0

    sentence_status = {}

    for string_cur in range(1, len(sentence)):

        for status_i in status_list:
            for status_j in status_list:

                if (status_j, sentence[string_cur]) in b:
                    launch_probability = b[(status_j, sentence[string_cur])]
                else:
                    launch_probability = 1e-10

                new_alpha = alpha[(string_cur - 1, status_i)] * a[(status_i, status_j)] * launch_probability

                if (alpha[(string_cur, status_j)] < new_alpha):
                    alpha[(string_cur, status_j)] = new_alpha
                    sentence_status[(string_cur, status_j)] = status_i

    end_f_cur = len(sentence)

    for status_i in status_list:

        new_alpha = alpha[(end_f_cur - 1, status_i)] * a[(status_i, 'f')]

        if (alpha[(end_f_cur, 'f')] < new_alpha):
            alpha[(end_f_cur, 'f')] = new_alpha
            sentence_status[(end_f_cur, 'f')] = status_i

    status = ""
    q = 'f'
    i = len(sentence)
    while i >= 1:
        q = sentence_status[(i, q)]
        status = q + status
        i -= 1
    output_result(sentence,status)
    return status


import math


def segment_log(sentence):
    alpha = {}  # 二维数组  结尾加一个ajf
    soft_probability=1e-7
    for i in range(len(sentence)):
        for status in status_list:
            if (i == 0):
                if a[('0', status)] == 0:
                    continue


                if (status, sentence[0]) in b:
                    launch_probability = b[(status, sentence[0])]
                else:
                    launch_probability = soft_probability
                alpha[(i, status)] = math.log2(a[('0', status)]) + math.log2(launch_probability)

    sentence_status = {}

    for string_cur in range(1, len(sentence)):

        for status_i in status_list:
            for status_j in status_list:
                if a[(status_i, status_j)]==0 or (string_cur - 1, status_i) not in alpha:
                    continue


                if (status_j, sentence[string_cur]) in b:
                    launch_probability = b[(status_j, sentence[string_cur])]
                else:
                    launch_probability = soft_probability

                new_alpha = alpha[(string_cur - 1, status_i)] + math.log2(a[(status_i, status_j)]) + math.log2(launch_probability)

                if ((string_cur, status_j) not in alpha or alpha[(string_cur, status_j)] < new_alpha):
                    alpha[(string_cur, status_j)] = new_alpha
                    sentence_status[(string_cur, status_j)] = status_i

    end_f_cur = len(sentence)

    for status_i in status_list:
        if a[(status_i, 'f')] == 0 or (end_f_cur - 1, status_i) not in alpha:
            continue
        new_alpha = alpha[(end_f_cur - 1, status_i)] + math.log2(a[(status_i, 'f')])

        if ((end_f_cur, 'f') not in alpha or alpha[(end_f_cur, 'f')] < new_alpha):
            alpha[(end_f_cur, 'f')] = new_alpha
            sentence_status[(end_f_cur, 'f')] = status_i

    status = ""
    q = 'f'
    i = len(sentence)
    while i >= 1:
        q = sentence_status[(i, q)]
        status = q + status
        i -= 1
    output_result(sentence,status)
    return status

def get_right_word_count(s1,s2):
    i=0
    count=0
    all=0
    start_pos1=0
    start_pos2=0
    while i<len(s1):
        if(s1[i]==s2[i] and s1[i]== 's'):
            count+=1

        if (s1[i] == s2[i] and s1[i] == 'e' and start_pos1==start_pos2):
            count += 1

        if(s2[i]=='e' or s2[i]=='s'):
            all+=1

        if(s1[i]=='b'):
            start_pos1=i
        if (s2[i] == 'b'):
            start_pos2 = i

        i+=1
    return count,all


def eval():
    all=0
    count=0
    for i in range(len(test_observation_status_list)):
        status_seq = segment_log(test_observation_status_list[i][0])
        temp_count,temp_all=get_right_word_count(status_seq,test_observation_status_list[i][1])
        count+=temp_count
        all+=temp_all
    print(count/all)

if __name__ == "__main__":
    load_sentence_list()
    load_observation_status_list()
    static_a()
    compute_a()
    static_b()
    compute_b()
    segment("在三峡坝区，在长江的岸边，一条宽阔笔直的大道纵贯东西。")
    eval()


