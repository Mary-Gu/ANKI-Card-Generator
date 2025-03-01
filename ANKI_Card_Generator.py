from openai import OpenAI
from os import path, makedirs
from sys import argv

API_KEY = ""
LANGUAGE = "English"
# What You Need to Change is API_KEY, LANGUAGE, and Base_URL
client = OpenAI(
    api_key=API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 读取文件
tempDIR = "temp"
input_filename = "initial_input.txt"
output_filename_txt = "Question_Output.txt"
output_final_filename_txt = "Final_Output.txt"
current_dir = path.dirname(path.realpath(argv[0]))

inputFilePath = path.join(current_dir, input_filename)
tempDIRPath = path.join(current_dir, tempDIR)
if not path.exists(tempDIRPath):
    makedirs(tempDIRPath)
outputFileQuestionPath = path.join(current_dir, tempDIR, output_filename_txt)
outputFileFinalTxtPath = path.join(current_dir, tempDIR, output_final_filename_txt)

def generateQuestion(inputFilePath, outputFileQuestionPath):
    print("inputFilePath: ", inputFilePath)
    print("outputFileQuestionPath: ", outputFileQuestionPath)
    with open(inputFilePath, "r", encoding="utf-8") as file:
        input_text = file.read()
        # 如果input太长，每段4096个字符
        max_chunk_size = 4096 * 2
    result = ""

    # 确定是否需要分块处理
    chunks = (
        [
            input_text[i : i + max_chunk_size]
            for i in range(0, len(input_text), max_chunk_size - 20)
        ]
        if len(input_text) > max_chunk_size
        else [input_text]
    )

    for i, chunk in enumerate(chunks):
        if len(chunks) > 1:
            print(f"处理第 {i+1}/{len(chunks)} 段文本")

        chunk_completion = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "你的任务是根据用户提供的文本信息，尽可能完善地、没有遗漏的生成带有上下文信息的问答题目，以帮助用户更好地掌握该文本所讲的信息。",
                },
                {
                    "role": "user",
                    "content": "你需要根据以下文本，用"+LANGUAGE+"生成对应的题目，给出所有知识点的、带有上下文信息的问答题目。请注意，不要生成不重要的信息的问答对："
                    + chunk,
                },
            ],
        )
        chunk_result = chunk_completion.choices[0].message.content
        result += chunk_result + "\n\n"
        ANKIresult = generateANKI(chunk_result, outputFileFinalTxtPath, writeOrNot=True)
        mode = "a" if i > 0 else "w"  # 第一次写入时清空文件，之后追加
        with open(outputFileQuestionPath, mode, encoding="utf-8") as file:
            file.write(chunk_result + "\n\n" if i < len(chunks) - 1 else chunk_result)
        with open(outputFileFinalTxtPath, mode, encoding="utf-8") as file:
            file.write(ANKIresult + "\n")
    # 如果是多段文本处理，最后一个额外的换行符可以移除
    if len(chunks) > 1:
        result = result.rstrip("\n")

    return result

def generateANKI(input_text, outputFileFinalTxtPath, writeOrNot=False):
    # inputQuestionFilePath
    # with open(inputQuestionFilePath, "r", encoding="utf-8") as file:
    #     input_text = file.read()
    if writeOrNot:
        completion = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """
                    你的任务是根据用户提供的题目和答案内容，生成 csv 格式的填空题，每个填空题互不关联，使用陈述句。每个题目以 csv 格式输出，每一行代表一个完整的包含填空部分的陈述句（题目）和答案。请严格按照以下要求生成内容：
                    1. 每一行均包含一个题目及其答案，不允许包含额外的说明、提示或其它字符（即整行仅为题目的内容）。
                    2. 题目和答案在同一行的两列中，以英语“, ”分隔为两列。包含填空部分的陈述句第一列（填空部分用下划线替代：____），答案在第二列（和下划线的答案一一对应），不要使用其它格式或符号。
                    3. 题目必须以填空的形式嵌入到句子中，被挖空的格式为“____”。
                    4. 你需要注意第一列和第二列的内容中，不要出现任何英文逗号，相反，你可以使用句号（。）或中文的逗号（，）来完成。
                    5. 题目的表达可以不同于原题目，你的首要目标是帮助用户通过题目更好地掌握知识，因此请尽可能设计清晰、有效的填空题。且题目需要为陈述句。
                    6. 填空的答案不要过长，保证题目的可回答性。每个题目的内容独立，使用陈述句，不要有上下文关联。
                    7. 输出不要包含其他任何内容，用引号包裹。

                    输出示例：
                    "原子的基本组成部分分别是：____、____、____. ", "质子，中子，电子"
                    "The repeating units in DNA are called ____.", "nucleotides"
                    "cell walls are made of ____, which is a complex ____.", cellulose. "carbohydrate"
                    "complex sugars are also called ____", "polysaccharides"
                    "polysaccharides is a kind of polymer, which is made of ____", "monosaccharides"


                    """.strip().replace(
                        " ", ""
                    ),
                },
                {
                    "role": "user",
                    "content": "<content>\n"
                    + input_text
                    + "\n <\content> \n"
                    + "你需要根据题目和回答，生成csv格式的字符串的填空题，用"
                    + LANGUAGE
                    + "生成，"
                    + """
                    仅回答csv格式的字符串即可，不要回答其他任何内容。带有填空部分的陈述句在第一列
                    （填空部分用下划线替代：____），答案在第二列（和下划线的答案一一对应）。
                    csv有且仅有两列，你需要注意第一列和第二列的内容中，不要出现任何英文逗号，
                    你可以使用句号（。）或中文的逗号（，）来完成。
                    填空部分尽可能短，不要过长，保证题目的可回答性。
                    请注意，每一个题目（陈述句）都必须至少有一个填空（____）部分！每个题目的内容独立，不要有上下文关联，也就是说，用户每次只能看见一行，前后文用户无法看见，所以必须一句话把条件说完整。
                    （这是示例）csv：
                    <example>
                    "原子的基本组成部分分别是：____、____、____. ", "质子，中子，电子"
                    "The repeating units in DNA are called ____.", "nucleotides"
                    "cell walls are made of ____, which is a complex ____.", cellulose. "carbohydrate"
                    "complex sugars are also called ____", "polysaccharides"
                    "polysaccharides is a kind of polymer, which is made of ____", "monosaccharides"
                    </example>
                    """.strip()
                    .replace("\n", "")
                    .replace(" ", ""),
                },
            ],
        )
        text = completion.choices[0].message.content
        # 第二轮确保生成的内容符合要求
        print(text)
        secondMessage = [
                {
                    "role": "system",
                    "content": """
                你的任务是根据用户提供的题目和答案内容，保证每一行均包含大于等于一个题目，及其答案，不允许包含额外的说明。
                """.strip().replace(
                        " ", ""
                    ),
                },
                {
                    "role": "user",
                    "content": "<content> \n"
                    + text
                    + "\n <\content> \n"
                    + """
                    上文是已经部分按照要求生成的内容，你需要根据信息，按照以下要求继续完善：
                    1. 仅回答csv格式的字符串即可，不要回答其他任何内容。
                    2. 问题部分使用**陈述句**。
                    3. 并去除无意义的问题。
                    4. 请注意，去掉所有引号，每一行的题目和答案之间用英文逗号分隔，并分行输出。
                    5. csv有且仅有**两列**，带有填空部分的陈述句在第一列（填空部分用下划线替代：____），（中间英语逗号分割）答案在第二列（和下划线的答案一一对应）。
                    6. 请注意，每一个题目（陈述句）都必须至少有一个填空（____）部分！
                    7. 每个题目的内容独立，不要有上下文关联，即：因为用户每次只能看见一行，前后文用户无法看见，所以必须一句话把条件说完整。
                    8. 对某一行没有挖空的题目，你需要自行设计填空，请保证填空的合理性和有效性。无论什么情况，都需要有“____”填空。
                    9. 对于某一行没有答案的题目，你需要自行设计答案，请保证答案的合理性和有效性。
                    10. 对于格式不正确的行，你需要自行调整，保证每一行均包含**至少一个题目**及**其答案**，不要减少题目的数量和内容。
                    （这是示例）csv：
                    <example>
                    "原子的基本组成部分分别是：____、____、____. ", "质子，中子，电子"
                    "The repeating units in DNA are called ____.", "nucleotides"
                    "cell walls are made of ____, which is a complex ____.", cellulose. "carbohydrate"
                    "complex sugars are also called ____", "polysaccharides"
                    "polysaccharides is a kind of polymer, which is made of ____", "monosaccharides"                    </example>
                    """.strip().replace(
                        " ", ""
                    ),
                },
            ]
        completion = client.chat.completions.create(
            model="qwen-turbo", temperature=0.6, messages=secondMessage
        )
        text2 = completion.choices[0].message.content
        secondMessage.append(
            {
                "role": "assistant",
                "content": text2,
            }
        )
        secondMessage.append(
            {
                "role": "user",
                "content": "请仔细检查格式是否正确，如果有任何问题，请继续修改并生成。",
            }
        )
        completion = client.chat.completions.create(
            model="qwen-turbo", temperature=0.6, messages=secondMessage
        )

    else:
        completion = client.chat.completions.create(
            model="qwen-turbo",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=[
                {
                    "role": "system",
                    "content": """
                    你的任务是根据用户提供的题目和答案内容，生成 txt 格式的填空题，每个题目以 csv 格式输出，每一行代表一个完整的题目。请严格按照以下要求生成内容：
                    1. 每一行均包含一个题目及其答案，不允许包含额外的说明、提示或其它字符（即整行仅为题目的内容）。
                    2. 答案必须以填空的形式嵌入到句子中，格式为 {{c1::答案}}，不要使用其它格式或符号。
                    3. 题目的表达可以不同于原题目，你的首要目标是帮助用户通过题目更好地掌握知识，因此请尽可能设计清晰、有效的填空题。
                    4. 一个题目中不要包含过多的空，空的数量应合理分布，保证题目整体的可读性和针对性。
                    5. 输出结果必须为纯文本（txt）形式，每个题目与答案占同一行，并且仅输出 csv 格式的字符串，不要包含其他任何内容。

                    例如：
                    原子的基本组成部分包括{{c1::质子}}、{{c1::中子}}、{{c1::电子}}。
                    """.strip()
                    .replace("\n", "")
                    .replace(" ", ""),
                },
                {
                    "role": "user",
                    "content": 
                    input_text
                    + "\n <content>"
                    + """
                    你需要根据题目和回答，生成txt格式的字符串的填空题，仅回答csv格式的字符串即可，不要回答其他任何内容。每一个题目与回答占同一行，答案均用{{c1::answer}}的方式嵌入到填空题的陈述句中。你的首要目标是帮助用户通过题目尽可能地掌握知识，所以不需要和原来的题的格式一样。只需要生成内容即可，请完整按照我所说的格式生成。句子前后不要有任何其他字符。例如：
                    ```text
                    这里是题目，这个是{{c1::填空的位置}}，填空的位置需要用括号括起来。
                    ```
                    示例：
                    ```text
                    原子的基本组成部分包括{{c1::质子}}、{{c1::中子}}、{{c1::电子}}。
                    ```
                    请直接输出题目和答案（即txt文本），一个题目中不要有太多空，请合理分开，但不要互相提示。不同题目均独立展示给学生，请勿有上下文关联。    """.strip()
                    .replace("\n", "")
                    .replace(" ", "")
                    + "\n <\content>\n"
                },
            ],
        )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content
    # with open(outputFileFinalTxtPath, "a", encoding="utf-8") as text_file:
    #     text_file.write(completion.choices[0].message.content)


if __name__ == "__main__":
    text = generateQuestion(inputFilePath, outputFileQuestionPath)
    #generateANKI(text, outputFileFinalTxtPath, writeOrNot=True)
