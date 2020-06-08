import torch

def loss_func(batch, net, tgt_net, GAMMA):
    states, actions, rewards, dones, next_states = batch

    states_v = torch.FloatTensor(states).to("cuda")
    next_states_v = torch.FloatTensor(next_states).to("cuda")
    actions_v = torch.LongTensor(actions).to("cuda")
    rewards_v = torch.FloatTensor(rewards).to("cuda")
    done_mask = torch.BoolTensor(dones).to("cuda")
    
    #Предсказание обучаемой сети
    state_action_values = net(states_v).gather(1, actions_v.unsqueeze(-1)).squeeze(-1) #action_v.unsqeeze(-1) вернет значения действия (они совпадут с индексами), squeeze соберет все в тензор
    
    #Предсказание обученной сети
    next_state_values = tgt_net(next_states_v).max(1)[0] #Вернет значения лучших Q
    next_state_values[done_mask] = 0.0 #Для завершившихся эпизодов следующее состояние имеет значение 0
    next_state_values = next_state_values.detach()

    expected_state_action_values = next_state_values * GAMMA + rewards_v #Ожидаемое значение Q согласно уравнению Белмана

    # return torch.nn.MSELoss(state_action_values, expected_state_action_values)
    squares = (state_action_values-expected_state_action_values)**2
    return squares.mean()#torch.nn.MSELoss(state_action_values, expected_state_action_values)

