import pandas as pd
import numpy as np
import copy

class MainLine:
    def __init__(self, config):
        self.config = config
        self.item_list = None
        self.item_list_initial = None
    
    def gene_fixed_sequence(self, batch_size=16):
        '''
        generate a fixed sequence in main machine
        '''
        item_list = []
        
        for item_code in (self.config.item_codes * 100):
            if(len(item_list) + batch_size <= self.config.main_max_num):
                item_list += [item_code for i in range(batch_size)]
            else:
                item_list += [item_code for i in range(self.config.main_max_num - len(item_list))]
                break
        self.item_list = item_list 
        self.item_list_initial = copy.deepcopy(self.item_list)
        # return self.item_list
    
    def get_next(self, remove_flag=True):
        item_code = self.item_list[0]
        if(remove_flag):
            self.item_list = self.item_list[1:]
        return item_code
    
    def get_next_type(self):
        item_code = self.item_list[0]
        for i in self.item_list:
            if(i != item_code):
                item_code = i
                break
        return item_code

    def get_after_num(self, item_code):
        '''
        get the direct item_code in item_list of main machine
        '''
        num = 0
        for i in self.item_list:
            if(i == item_code):
                num += 1
            else:
                break
        return num

class ComponentLine:
    def __init__(self, config):
        self.config = config
        self.schedule_list = list()
        self.est_start_time = 0
        self.est_finish_time = self.est_start_time + self.config.component_time
        self.schedule_item_code = self.config.item_codes[0]
        self.batch_now = 0

    def finish(self, component_buffer, t):
        self.schedule_list.append(self.schedule_item_code)
        self.batch_now += 1
        # estimate the start and finish time of nest component
        self.est_start_time = self.est_finish_time
        self.est_finish_time = self.est_start_time + self.config.component_time

        component_buffer.in_bound(self.schedule_item_code, t)

    def start(self, item_code):
        if(item_code != self.schedule_item_code):
            self.schedule_list.append(' ')
            self.schedule_item_code = item_code
            # add a changeover_time to the estimating start and finish time
            self.est_start_time += self.config.changeover_time
            self.est_finish_time += self.config.changeover_time
    
class Buffer:
    def __init__(self, config, buffer_size=10):
        self.buffer_size = buffer_size
        self.buffers = dict()
        self.max_buffer_size = dict()
        self.buffer_records = list()
        for item_code in config.item_codes:
            self.buffers[item_code] = buffer_size
            self.max_buffer_size[item_code] = buffer_size

    def out_bound(self, item_code, t):
        if(self.buffers[item_code] == 0):
            return False
        self.buffers[item_code] -= 1
        self.buffer_records.append([t, item_code, -1, self.buffers[item_code]])
        return True

    def in_bound(self, item_code, t):
        self.buffers[item_code] += 1
        self.buffer_records.append([t, item_code, 1, self.buffers[item_code]])
        # update the max buffer_size
        self.max_buffer_size[item_code] = max(self.max_buffer_size[item_code], \
                                            self.buffers[item_code])

class Simulation:
    def __init__(self, main_line, component_line, component_buffer, config):
        self.main_line = main_line
        self.component_line = component_line
        self.component_buffer = component_buffer
        self.config = config
        self.item_codes_finished = None
    def start(self):
        item_codes_finished = list()
        total_T = (self.config.main_max_num - 1) * self.config.item_time
        for t in range(total_T + 1):
            
            # product the main item
            if(t % self.config.item_time == 0):
                item_code = self.main_line.get_next()
                flag = self.component_buffer.out_bound(item_code, t)
                if(flag == False):
                    break
                else:
                    item_codes_finished.append(item_code)
            
            # product the component
            if(t == self.component_line.est_finish_time):
                self.component_line.finish(self.component_buffer, t)
                if(self.component_line.batch_now == self.config.batch_size):
                    # component scheduling strategy
                    fill_flag = True

                    if(fill_flag and True):
                        # strategy one
                        '''
                        select the minimal buffer of component to schedule
                        '''
                        sort_buffer = sorted(self.component_buffer.buffers.items(), \
                                            key = lambda x : x[1])
                        # print(sort_buffer)
                        # print(self.main_line.get_next_type())
                        if(sort_buffer[0][1] < self.config.buffer_left_epsilon):
                            self.component_line.start(sort_buffer[0][0])
                            fill_flag = False
                            print('strategy one')
                    if(fill_flag and True):
                        # strategy two
                        '''
                        ensure the gap between main_line and component_line will not be too large
                        '''
                        gap = self.main_line.get_after_num(self.component_line.schedule_item_code)
                        if(gap > self.config.gap_epsilon):
                            fill_flag = False
                            print('strategy two_1')
                        elif(gap == 0):
                            self.component_line.start(self.main_line.get_next(remove_flag=False))
                            fill_flag = False
                            print('strategy two_2')
                    if(fill_flag):
                        # schedule the next item in main_line
                        self.component_line.start(self.main_line.get_next_type())
                        print('strategy three')

                    print(self.main_line.get_next_type())
                    # reset the batch_now of component_line
                    self.component_line.batch_now = 0

        self.item_codes_finished = item_codes_finished
    
    # def start_unwait(self):
    #     '''
    #     Simulation runs
    #     '''
    #     item_codes_finished = list()
    #     while(len(self.main_line.item_list) != 0):
    #         # the item needs the component in the beginning of manufacturing
    #         item_code = self.main_line.get_next()
    #         flag = self.component_buffer.out_bound(item_code)
    #         if(flag == False):
    #             break
    #         else:
    #             item_codes_finished.append(item_code)
            
    #         # component_line has (0,51] seconds to do scheduling action

    def view(self):
        print('total length of main machine:%d' % self.config.main_max_num)
        print('scheduling length of main machine:%d' % len(self.item_codes_finished))
        print('max buffer size', self.component_buffer.max_buffer_size)

class Config:
    def __init__(self, item_type, main_max_num, buffer_left_epsilon, gap_epsilon):
        self.item_type = item_type
        self.item_codes = 'ABCDEFGHIJKLMN'[0:self.item_type]

        self.batch_size = 10
        self.changeover_time = 20
        self.component_time = 49
        self.item_time = 51

        self.main_max_num = main_max_num

        # change strategy
        self.buffer_left_epsilon = buffer_left_epsilon
        self.gap_epsilon = gap_epsilon

if(__name__ == '__main__'):
    '''
    Parameters:
        item_type : the number of item type
        main_max_num : simulate main_max_num items
        batch_size : the simutation of main_line sequence
        buffer_size : initial buffer of every component
        buffer_left_epsilon : if the buffer of component is less than buffer_left_epsilon, schedule it
        gap_epsilon : if the gap is great or eauql than gap_epsilon, schedule the relative cmponent
    '''
    # experiment config
    config = Config(item_type=6 ,main_max_num=1000, buffer_left_epsilon=4, gap_epsilon=6)
    # main line
    main_line = MainLine(config)
    main_line.gene_fixed_sequence(batch_size=16)
    # component line
    component_line = ComponentLine(config)
    # buffer
    component_buffer = Buffer(config, buffer_size=10)
    # Simulation
    example = Simulation(main_line, component_line, component_buffer, config)
    example.start()
    # result viewing and saving
    example.view()
    df_main_line = pd.DataFrame(main_line.item_list_initial)
    df_main_line.to_excel('main_line.xlsx')
    df_component_use = pd.DataFrame(component_buffer.buffer_records, columns=['t', 'component', 'flag', 'buffer'])
    df_component_use.to_excel('component_schedule.xlsx')

    print('finished')