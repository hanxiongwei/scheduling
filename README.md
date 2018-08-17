# scheduling
cityu

part_one<20180817>:
	支持主线连续性的序列，策略方面有三类：
		策略一：buffer小于一定值时，触发补货
		策略二：gap大于一定值时，触发补货
		策略三：策略一+策略二，另两个策略的参数之和为10（component batch_size）
	Parameters:
        item_type : the number of item type
        main_max_num : simulate main_max_num items
        batch_size : the simutation of main_line sequence
        buffer_size : initial buffer of every component
        buffer_left_epsilon : if the buffer of component is less than buffer_left_epsilon, schedule it
        gap_epsilon : if the gap is great or eauql than gap_epsilon, schedule the relative cmponent
		
