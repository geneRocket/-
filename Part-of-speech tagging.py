

observation_status_list=[]
test_observation_status_list=[]
status_list=set()

def get_word_tag_list(sentence):
    ret=[]
    word_tag_list=sentence.strip().split()[1:]


    for word_tag in word_tag_list:
        if word_tag.startswith('['):
            word_tag=word_tag[1:]
        elif ']' in word_tag:
            word_tag=word_tag[:word_tag.index(']')]

        ret.append(word_tag)
    return ret


def load_sentence_list():
    with open('1998-01-105-带音.txt',"r",encoding='gbk') as f:
        for idx,line in enumerate(f):
            word_tag_list=get_word_tag_list(line)
            if len(word_tag_list)==0:
                continue

            word_list=[word_tag.split('/')[0] for word_tag in word_tag_list]



            tag_list=[word_tag.split('/')[1] for word_tag in word_tag_list]


            status_list.update(set(tag_list))

            if idx % 10 < 8:
                observation_status_list.append((word_list, tag_list))
            else:
                test_observation_status_list.append((word_list, tag_list))

    print(len(observation_status_list))
    print(len(test_observation_status_list))



def output_result(observation, status):



    list=""
    for i,status in enumerate(status):
        if(i>=len(observation)):
            break

        list+=observation[i]
        list+='/'
        list+=status
        list+=' '


    print(list)





a_fenmu={}
a_fenzi={}

def init_a_fenmu_fenzi():
    for status in status_list:
        a_fenmu[status]=0
    a_fenmu['0']=0


    for status_i in status_list:
        for status_j in status_list:
            a_fenzi[(status_i,status_j)]=0

        a_fenzi[('0',status_i)]=0
        a_fenzi[(status_i,'f')]=0



def static_a():
    for observation,status in observation_status_list:
        for i in range(1,len(status)):
            a_fenmu[status[i-1]]+=1
            a_fenzi[(status[i-1],status[i])]+=1

        a_fenmu['0'] += 1
        a_fenzi[('0', status[0])] += 1

        a_fenmu[status[-1]]+=1
        a_fenzi[(status[-1],'f')]+=1



a={}
def compute_a():
    for status_i in status_list:
        for status_j in status_list:
            if a_fenmu[status_i]!=0:
                a[(status_i,status_j)]=a_fenzi[(status_i,status_j)]/a_fenmu[status_i]

        a[('0', status_i)] = a_fenzi[('0', status_i)]/a_fenmu['0']

        if a_fenmu[status_i] != 0:
            a[(status_i,'f')] = a_fenzi[( status_i,'f')] / a_fenmu[status_i]




b_fenmu={}
b_fenzi={}

def static_b():
    for observation,status in observation_status_list:
        for i in range(len(status)):
            q=status[i]
            o=observation[i]
            if q not in b_fenmu:
                b_fenmu[q]=0
            b_fenmu[q]+=1
            if (q,o) not in b_fenzi:
                b_fenzi[(q,o)]=0
            b_fenzi[(q,o)]+=1

b={}
def compute_b():
    for (q,o) in b_fenzi:
        b[(q,o)]=b_fenzi[(q,o)]/b_fenmu[q]



import math
def part_of_speech_tagging(sentence):
    alpha={} # 二维数组   结尾加一个ajf

    for status in status_list:
        if ('0',status) not in a:
            continue
        if a[('0',status)]==0:
            continue

        if (status,sentence[0]) in b:
            launch_probability=b[(status,sentence[0])]
        else:
            launch_probability = 1e-10

        alpha[(0,status)]=math.log2(a[('0',status)])+math.log2(launch_probability)




    sentence_status={}  # 二维数组  结尾加一个f  由哪一个状态转过来的


    for string_cur in range(1,len(sentence)):
        for status_i in status_list:
            for status_j in status_list:
                if (status_i, status_j) not in a:
                    continue
                if a[(status_i, status_j)]==0:
                    continue
                if (string_cur - 1, status_i) not in alpha:
                    continue


                if (status_j,sentence[string_cur]) in b:
                    launch_probability=b[(status_j,sentence[string_cur])]
                else:
                    launch_probability = 1e-10


                new_alpha = alpha[(string_cur - 1, status_i)] + math.log2(a[(status_i, status_j)]) + math.log2(launch_probability)

                if((string_cur,status_j) not in alpha or alpha[(string_cur,status_j)]<new_alpha):
                    alpha[(string_cur,status_j)] = new_alpha
                    sentence_status[(string_cur,status_j)]=status_i

    end_f_cur=len(sentence)
    for status_i in status_list:
        if (status_i, 'f') not in a:
            continue
        if a[(status_i, 'f')]==0:
            continue
        if (end_f_cur - 1, status_i) not in alpha:
            continue
        new_alpha = alpha[(end_f_cur-1, status_i)] +  math.log2(a[(status_i, 'f')])

        if ((end_f_cur, 'f') not in alpha or alpha[(end_f_cur, 'f')] < new_alpha):
            alpha[(end_f_cur, 'f')] = new_alpha
            sentence_status[(end_f_cur, 'f')] = status_i

    status=[]
    q='f'
    i=len(sentence)
    while i>=1:
        q=sentence_status[(i,q)]
        status=[q]+status
        i-=1
    output_result(sentence,status)
    return status

def get_right_tag_count(s1, s2):
    i=0
    count=0
    all=0

    while i<len(s1):
        if(s1[i]==s2[i]):
            count+=1
        all+=1
        i+=1
    return count,all


def eval():
    all=0
    count=0
    for i in range(len(test_observation_status_list)):
        status_seq = part_of_speech_tagging(test_observation_status_list[i][0])
        temp_count,temp_all=get_right_tag_count(status_seq, test_observation_status_list[i][1])
        count+=temp_count
        all+=temp_all
        print(count/all)

if __name__=="__main__":
    load_sentence_list()
    init_a_fenmu_fenzi()
    static_a()
    compute_a()
    static_b()
    compute_b()
    part_of_speech_tagging(observation_status_list[0][0])
    part_of_speech_tagging(['本报', '驻', '加拿大', '记者', '邹', '德浩'])
    part_of_speech_tagging(['跨', '过', '岁末', '的', '最后', '一', '道', '门槛'])
    eval()