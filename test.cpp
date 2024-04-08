#include <iostream>
#include <array>
#include <vector>
#include <cstdlib>
#include <chrono>
#include <thread>
#include <cmath>

using namespace std;

struct ScreenData {
    array<int, 2> coords;
    vector<vector<char>> screen;
    array<int, 2> center;
};


ScreenData create_screen() {
    ScreenData data;
    data.coords = { 50, 50 };
    data.screen = vector<vector<char>>(50, vector<char>(50, '-'));
    data.center = { 25, 25 };
    return data;
}

vector<vector<array<int, 2>>> squareShape(const ScreenData  screenData, int square_size) {
    int center_x = screenData.center[0];
    int center_y = screenData.center[1];
    int half_square_size = static_cast<int>(round(square_size / 2));
    vector<vector<array<int, 2>>> coords(4, vector<array<int, 2>>(square_size));
    for (int i = 0; i < square_size; ++i) {
        coords[0][i] = { center_x - half_square_size, center_y - half_square_size + i };
        coords[1][i] = { center_x + half_square_size, center_y - half_square_size + i };
        coords[2][i] = { center_x - half_square_size + i, center_y - half_square_size };
        coords[3][i] = { center_x - half_square_size + i, center_y + half_square_size };
    }

    return coords;
}
array<int, 2> rotate_shape(int x, int y, int center, int angle) {
    double radians = angle * 3.1415 / 180;
    int new_x = static_cast<int>(floor((x - center) * cos(radians) - (y - center) * sin(radians)) + center);
    int new_y = static_cast<int>(floor((x - center) * sin(radians) + (y - center) * cos(radians)) + center);
    array<int, 2> new_points = { new_x, new_y };
    return new_points;
}
vector<vector<char>> printShape(vector<vector<array<int, 2>>> coords, const ScreenData screenData, int angle) {
    vector<vector<char>> result(screenData.screen.size(), vector<char>(screenData.screen[0].size(), '-'));
    for (int i = 0; i < 4; i++) {
        for (const auto coord : coords[i]) {
            int x = coord[0];
            int y = coord[1];
            if (0 <= x && x < 50 && 0 <= y && y < 50) {
                array<int, 2> new_points =  rotate_shape(x, y, screenData.center[0], angle);
                result[new_points[0]][new_points[1]] = 'X';
            }
        }
    }
    return result;
};



int main() {
    int j = 1;
    int change_size = 1;
    int angle = 0;
    ScreenData screenData = create_screen();
    while (true) {
        if (j > 30) {change_size = -1;}
        if (j == 0) { change_size = 1; }
        if (angle > 360) { angle = 0; }
        vector<vector<array<int, 2>>> coords = squareShape(screenData, j);
        vector<vector<char>> screen = printShape(coords, screenData, angle);
        for (const auto& row : screen) {
            for (char element : row) {
                cout << element << " ";
            }
            cout << endl;
        }
        j = j + change_size;
        angle++;
        this_thread::sleep_for(chrono::milliseconds(1000 / 60));
        system("cls");
         

    }
    return 0;
    }