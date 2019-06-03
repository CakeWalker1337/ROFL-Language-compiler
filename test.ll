


define i32 @main() {
    %n.ptr = alloca i32
    store i32 5, i32* %n.ptr
    %counter.ptr = alloca i32
    store i32 1, i32* %counter.ptr
    %arr.ptr = alloca [123 x i32]
    br label %lab.0
lab.0:
    %counter.1 = load i32, i32* %counter.ptr
    %n.2 = load i32, i32* %n.ptr
    %buffer3 = icmp slt i32 %counter.1, %n.2
    br i1 %buffer3, label %lab.1, label %lab.2
lab.1:
    %counter.4 = load i32, i32* %counter.ptr
    %arr.5.ptr = getelementptr inbounds [123 x i32], [123 x i32]* %arr.ptr, i32 0, i32 %counter.4
    %counter.6 = load i32, i32* %counter.ptr
    store i32 %counter.6, i32* %arr.5.ptr
    %counter.7 = load i32, i32* %counter.ptr
    %arr.8.ptr = getelementptr inbounds [123 x i32], [123 x i32]* %arr.ptr, i32 0, i32 %counter.7
    %buffer9 = load i32, i32* %arr.8.ptr
    %buffer10 = getelementptr inbounds [4 x i8], [4 x i8]* @.str.1, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer10, i32 %buffer9)
    %counter.11 = load i32, i32* %counter.ptr
    %buffer12 = add i32 %counter.11, 1
    store i32 %buffer12, i32* %counter.ptr
    br label %lab.0
lab.2:
    ret i32 0
}

declare i32 @printf(i8*, ...)
@.str.1 = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
