import re
import pandas as pd

def parse_fio_output(output,write_percent):
    result = {}

    if write_percent == 'write100':
        #================================================ write ================================================
        # write IOPS 추출
        write_iops_match = re.search(r'write: IOPS=(\d+\.?\d*)', output)
        if write_iops_match:
            result['write IOPS(k)'] = float(write_iops_match.group(1))

        # write clat avg, stdev, max, min 추출
        clat_attributes = re.findall(r'clat \(usec\): min=(\d+\.?\d*\S*), max=(\d+\.?\d*\S*), avg=(\d+\.?\d*\S*), stdev=(\d+\.?\d*\S*)', output)
        #print(clat_attributes)
        # print(clat_attributes[0])
        # print(clat_attributes[1])
        result['write min(usec)'] = float(clat_attributes[0][0])
        if clat_attributes[0][1][-1] == 'k':
            result['write max(usec)'] = float(clat_attributes[0][1][:-1]) * 1000
        else:
            result['write max(usec)'] = float(clat_attributes[0][1])
        result['write avg(usec)'] = float(clat_attributes[0][2])
        result['write stdev(usec)'] = float(clat_attributes[0][3])

        # write clat percentiles 추출
        percentile_matches = re.findall(r'(\d+.\d+)th=\[\s*(\d+)\s*\]', output)
        # print(percentile_matches[0])
        # print(percentile_matches[1])
        for percentile_match in percentile_matches[0:17]:
            percentile = percentile_match[0]
            latency = int(percentile_match[1])
            result['write ' + percentile + ' th(usec)'] = latency
        # print(percentile_matches)

    elif write_percent != 'write100' and write_percent != 'write0':
        # write IOPS 추출
        write_iops_match = re.search(r'write: IOPS=(\d+\.?\d*)', output)
        if write_iops_match:
            result['write IOPS(k)'] = float(write_iops_match.group(1))

        # write clat avg, stdev, max, min 추출
        clat_attributes = re.findall(r'clat \(usec\): min=(\d+\.?\d*\S*), max=(\d+\.?\d*\S*), avg=(\d+\.?\d*\S*), stdev=(\d+\.?\d*\S*)', output)
        #print(clat_attributes)
        # print(clat_attributes[0])
        # print(clat_attributes[1])
        result['write min(usec)'] = float(clat_attributes[0][0])
        if clat_attributes[0][1][-1] == 'k':
            result['write max(usec)'] = float(clat_attributes[0][1][:-1]) * 1000
        else:
            result['write max(usec)'] = float(clat_attributes[0][1])
        result['write avg(usec)'] = float(clat_attributes[0][2])
        result['write stdev(usec)'] = float(clat_attributes[0][3])

        # write clat percentiles 추출
        percentile_matches = re.findall(r'(\d+.\d+)th=\[\s*(\d+)\s*\]', output)
        # print(percentile_matches[0])
        # print(percentile_matches[1])
        for percentile_match in percentile_matches[0:17]:
            percentile = percentile_match[0]
            latency = int(percentile_match[1])
            result['write ' + percentile + ' th(usec)'] = latency
        # print(percentile_matches)

        #================================================ read ================================================
        # read IOPS 추출
        read_iops_match = re.search(r'read: IOPS=(\d+\.?\d*)', output)
        if read_iops_match:
            result['read IOPS(k)'] = float(read_iops_match.group(1))

        # read clat avg, stdev, max, min 추출
        result['read min(usec)'] = float(clat_attributes[1][0])
        if clat_attributes[0][1][-1] == 'k':
            result['read max(usec)'] = float(clat_attributes[1][1][:-1]) * 1000
        else:
            result['read max(usec)'] = float(clat_attributes[1][1])
        result['read avg(usec)'] = float(clat_attributes[1][2])
        result['read stdev(usec)'] = float(clat_attributes[1][3])

        for percentile_match in percentile_matches[17:34]:
            percentile = percentile_match[0]
            latency = int(percentile_match[1])
            result['read ' + percentile + ' th(usec)'] = latency

    elif write_percent == 'write0':
        #================================================ read ================================================
        # read IOPS 추출
        read_iops_match = re.search(r'read: IOPS=(\d+\.?\d*)', output)
        if read_iops_match:
            result['read IOPS(k)'] = float(read_iops_match.group(1))

        clat_attributes = re.findall(r'clat \(usec\): min=(\d+\.?\d*\S*), max=(\d+\.?\d*\S*), avg=(\d+\.?\d*\S*), stdev=(\d+\.?\d*\S*)', output)

        # read clat avg, stdev, max, min 추출
        result['read min(usec)'] = float(clat_attributes[0][0])
        if clat_attributes[0][1][-1] == 'k':
            result['read max(usec)'] = float(clat_attributes[0][1][:-1]) * 1000
        else:
            result['read max(usec)'] = float(clat_attributes[0][1])
        result['read avg(usec)'] = float(clat_attributes[0][2])
        result['read stdev(usec)'] = float(clat_attributes[0][3])

        percentile_matches = re.findall(r'(\d+.\d+)th=\[\s*(\d+)\s*\]', output)
        for percentile_match in percentile_matches[0:17]:
            percentile = percentile_match[0]
            latency = int(percentile_match[1])
            result['read ' + percentile + ' th(usec)'] = latency

    return result

def parse_fio_files(file_paths):
    parsed_results = {}
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            fio_output = file.read()

            # Extract write_percent from filename
            write_percent = file_path.split(sep='_')[0]
            queue_depth = re.sub(".txt", "", file_path.split(sep='_')[3])

            if write_percent not in parsed_results:
                parsed_results[write_percent] = []

            parsed_results[write_percent].append((queue_depth, parse_fio_output(fio_output,write_percent)))
    return parsed_results

file_paths=[]
for write_percent in ("100","50", "0"):
    for queue_depth in ("1" ,"2"):
        file_paths.append("write"+write_percent+"_fio_output_QD"+queue_depth+".txt")

# 파일 파싱
parsed_results = parse_fio_files(file_paths)

# 데이터프레임 생성 및 결과 내보내기
with pd.ExcelWriter('fio_results.xlsx') as writer:
    for write_percent, results in parsed_results.items():
        dfs = []
        for queue_depth, result in results:
            result['Queue Depth'] = queue_depth
            df = pd.DataFrame([result])
            dfs.append(df)
        final_df = pd.concat(dfs, ignore_index=True)
        final_df.set_index('Queue Depth', inplace=True)
        final_df = final_df.transpose()
        final_df.to_excel(writer, sheet_name=write_percent)
