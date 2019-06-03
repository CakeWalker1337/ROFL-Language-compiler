


define i32 @main() {
    %c.ptr = alloca [10 x i32]
    %c.1.ptr = getelementptr inbounds [10 x i32], [10 x i32]* %c.ptr, i32 0, i32 0
    store i32 1, i32* %c.1.ptr
    %c.2.ptr = getelementptr inbounds [10 x i32], [10 x i32]* %c.ptr, i32 0, i32 1
    store i32 -3, i32* %c.2.ptr
    %c.3.ptr = getelementptr inbounds [10 x i32], [10 x i32]* %c.ptr, i32 0, i32 2
    store i32 4, i32* %c.3.ptr
    %c.4.ptr = getelementptr inbounds [10 x i32], [10 x i32]* %c.ptr, i32 0, i32 3
    store i32 2, i32* %c.4.ptr
    %c.5.ptr = getelementptr inbounds [10 x i32], [10 x i32]* %c.ptr, i32 0, i32 4
    store i32 -9, i32* %c.5.ptr
    %c.6.ptr = getelementptr inbounds [10 x i32], [10 x i32]* %c.ptr, i32 0, i32 5
    store i32 12, i32* %c.6.ptr
    %c.7.ptr = getelementptr inbounds [10 x i32], [10 x i32]* %c.ptr, i32 0, i32 6
    store i32 5, i32* %c.7.ptr
    %c.8.ptr = getelementptr inbounds [10 x i32], [10 x i32]* %c.ptr, i32 0, i32 7
    store i32 3, i32* %c.8.ptr
    %c.9.ptr = getelementptr inbounds [10 x i32], [10 x i32]* %c.ptr, i32 0, i32 8
    store i32 1, i32* %c.9.ptr
    %c.10.ptr = getelementptr inbounds [10 x i32], [10 x i32]* %c.ptr, i32 0, i32 9
    store i32 5, i32* %c.10.ptr
    %count.ptr = alloca i32
    store i32 0, i32* %count.ptr
    %sum.ptr = alloca i32
    store i32 0, i32* %sum.ptr
    br label %lab.0
lab.0:
    %count.11 = load i32, i32* %count.ptr
    %buffer12 = icmp slt i32 %count.11, 10
    br i1 %buffer12, label %lab.1, label %lab.2
lab.1:
    %count.13 = load i32, i32* %count.ptr
    %buffer14 = srem i32 %count.13, 2
    %buffer15 = icmp eq i32 %buffer14, 1
    %count.16 = load i32, i32* %count.ptr
    %c.17.ptr = getelementptr inbounds [10 x i32], [10 x i32]* %c.ptr, i32 0, i32 %count.16
    %c.17.18 = load i32, i32* %c.17.ptr
    %buffer19 = icmp sgt i32 %c.17.18, 0
    %buffer20 = and i1 %buffer15, %buffer19
    br i1 %buffer20, label %lab.3, label %lab.4
lab.3:
    %sum.21 = load i32, i32* %sum.ptr
    %count.22 = load i32, i32* %count.ptr
    %c.23.ptr = getelementptr inbounds [10 x i32], [10 x i32]* %c.ptr, i32 0, i32 %count.22
    %c.23.24 = load i32, i32* %c.23.ptr
    %buffer25 = add i32 %sum.21, %c.23.24
    store i32 %buffer25, i32* %sum.ptr
    br label %lab.5
lab.4:
    br label %lab.5
lab.5:
    %count.26 = load i32, i32* %count.ptr
    %buffer27 = add i32 %count.26, 1
    store i32 %buffer27, i32* %count.ptr
    br label %lab.0
lab.2:
    %sum.28 = load i32, i32* %sum.ptr
    %buffer30 = getelementptr inbounds [17 x i8], [17 x i8]* @.str.2, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer30, i32 %sum.28)
    ret i32 0
}

declare i32 @printf(i8*, ...)
@.str.1 = private unnamed_addr constant [14 x i8] c"The sum is - \00", align 1
@.str.2 = private unnamed_addr constant [17 x i8] c"The sum is - %d\0A\00", align 1
