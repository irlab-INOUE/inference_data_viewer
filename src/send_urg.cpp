#include <iostream>
#include "zmq.hpp"
//#include "GetUrg3d.h"

int main(int argc, char *argv[]) {

	// ZMQ setting
	zmq::context_t context(1);
	zmq::socket_t socket(context, zmq::socket_type::req);
	socket.connect("tcp://localhost:5555");
	std::cout << "Start zmq server.\n";

	/*
	// 3D-LiDAR setting
	std::string addr = "172.16.20.214";
	long port = 10904;
	GetUrg3d urg3d(addr, port);
	if(urg3d.initUrg3d() == -1) {
		std::cerr << "Error: Can't open 3D-LiDAR. Stoped." << std::endl;
		return -1;
	}
	*/

	while(true){
		// trigger
		std::cout << "Press Enter";
		std::cin.get();

		// Send LiDAR data
		std::cout << "Sending LiDAR data...\n";
		std::vector<pointUrg3d> data = urg3d.get1Frame();
		// y, z は-符号をつけることで3D-LiDARの実装と同じ向きになる
		// この段階では逆さまの状態で値を保存している

		size_t size = data.size();
		zmq::message_t msg_data_size((void*)&size, sizeof(size_t), NULL);
		auto res = socket.send(msg_data_size, zmq::send_flags::none);
		zmq::message_t rcv_msg_data_size;
		res = socket.recv(msg_data_size, zmq::recv_flags::none);

		for (int i = 0; i < data.size(); i++) {
			zmq::message_t msg((void*)&data[i], sizeof(pointUrg3d), NULL);
			auto recv = socket.send(msg, zmq::send_flags::none);

			zmq::message_t rcv_msg;
			auto recv2 = socket.recv(rcv_msg, zmq::recv_flags::none);
			std::string rpl = std::string(static_cast<char*>(rcv_msg.data()), rcv_msg.size());
		}
		std::cout << "finish.\n";
	}
	return 0;
}

