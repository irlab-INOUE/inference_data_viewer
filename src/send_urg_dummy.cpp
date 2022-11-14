#include <iostream>
#include "zmq.hpp"
#include <random>
#include <math.h>
std::random_device rd;
std::default_random_engine eng(rd());
std::uniform_real_distribution<float> rd_r(1.00, 3.00);		// 1.00 ~ 3.00
std::uniform_real_distribution<float> rd_t(-M_PI/2, M_PI/2);		// 1.00 ~ 3.00
std::uniform_real_distribution<float> rd_z(1.00, 1.10);		// 1.00 ~ 1.10
std::uniform_int_distribution<int> rd_i(0, 1599);			// 0 ~ 1599


typedef struct { 
    double x;
    double y;
    double z;
    double r;       // range
    double phi;     // vertical rad
    double theta;   // horizontal rad
    double i;       // refrection intensity
} pointUrg3d; 

int main(int argc, char *argv[]) {

	// ZMQ setting
	zmq::context_t context(1);
	zmq::socket_t socket(context, zmq::socket_type::req);
	socket.connect("tcp://localhost:5555");
	std::cout << "Start zmq server.\n ----- \n";

	double r, t;

	while(true){
		// trigger
		std::cout << "Press Enter";
		std::cin.get();

		// Send LiDAR data
		std::cout << "Sending LiDAR data..." << std::flush;
		size_t size = 20000;
		std::vector<pointUrg3d> data;
		for (int i = 0; i < size; i++){
			pointUrg3d p;
			r = rd_r(eng);
			t = rd_t(eng);
			p.x = r * cos(t);
			p.y = r * sin(t);
			p.z = rd_z(eng);
			p.r = 0;
			p.phi = 0;
			p.theta = 0;
			p.i = rd_i(eng);
			data.push_back(p);
		}
		// y, z は-符号をつけることで3D-LiDARの実装と同じ向きになる
		// この段階では逆さまの状態で値を保存している

		zmq::message_t msg_data_size((void*)&size, sizeof(size_t), NULL);
		auto res = socket.send(msg_data_size, zmq::send_flags::none);
		zmq::message_t rcv_msg_data_size;
		res = socket.recv(msg_data_size, zmq::recv_flags::none);

		for (int i = 0; i < size; i++) {
			zmq::message_t msg((void*)&data[i], sizeof(pointUrg3d), NULL);
			auto recv = socket.send(msg, zmq::send_flags::none);

			zmq::message_t rcv_msg;
			auto recv2 = socket.recv(rcv_msg, zmq::recv_flags::none);
			std::string rpl = std::string(static_cast<char*>(rcv_msg.data()), rcv_msg.size());
		}
		std::cout << " finish.\n -----  \n";
	}
	return 0;
}

